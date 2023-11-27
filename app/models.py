from app import db, login_manager
from datetime import datetime
from sqlalchemy import ForeignKeyConstraint
from flask_login import UserMixin
from sqlalchemy import event, ARRAY

user_system = db.Table('user_system',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('system_id', db.Integer, db.ForeignKey('system.id'))
                    )

devicetype_parameter = db.Table('devicetype_parameter',
                    db.Column('device_type_id', db.Integer, db.ForeignKey('device_type.id')),
                    db.Column('parameter_id', db.Integer, db.ForeignKey('parameter.id'))
                    )

request_system = db.Table('request_system',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('system_id', db.Integer, db.ForeignKey('system.id'))
                    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    #PK
    id = db.Column(db.Integer, primary_key=True)                     
    username = db.Column(db.String(20), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128),nullable =False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    role = db.Column(db.String(30),nullable = False)


    # 1:N create values
    values = db.relationship('Value',backref="user")
    # 1:N manage devices
    devices = db.relationship('Device',backref="user",cascade='all, delete')
    # 1:N manage systems
    managed_systems = db.relationship('System',backref="user",cascade='all, delete')
    # N:M used systems
    used_systems = db.relationship('System',secondary=user_system,backref='users')
    # 1:N defined kpis
    defined_kpi = db.relationship('Kpi',backref="user")

    # N:M request system use
    request_system = db.relationship('System',secondary=request_system,backref='users_requesting')

    @classmethod
    def delete(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()

    @classmethod
    def get_all(cls):
        users = User.query.all()
        return users


class System(db.Model):
    __tablename__ = "system"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique = True,nullable = False)
    description = db.Column(db.String(200))

    # owner/ manager of system
    system_manager = db.Column(db.Integer,db.ForeignKey('user.id'))


    # 1:N system devices
    devices = db.relationship('Device',backref="system_back_ref",cascade='all, delete')

    # 1:N system kpi
    kpis = db.relationship('Kpi',backref="system_back_ref_2",cascade='all, delete')

    #M:N users systems already define in User

class Device(db.Model):
    __tablename__ = "device"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable =False)
    description = db.Column(db.String(200))
    
    #device owner/manager
    device_manager = db.Column(db.Integer,db.ForeignKey('user.id'))
    #system
    system = db.Column(db.Integer,db.ForeignKey('system.id'))
    # 1:N device values
    values = db.relationship('Value',backref="device_back_ref",cascade='all, delete')

    #device type
    device_type_id = db.Column(db.Integer,db.ForeignKey('device_type.id'))


class DeviceType(db.Model):
    __tablename__ = "device_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable = False)

    parameters = db.relationship('Parameter',secondary="devicetype_parameter",backref='device_types')


    #devices that are this device type
    devices = db.relationship('Device',backref="device_type_back_ref_2",cascade='all, delete')





class Parameter(db.Model):
    __tablename__ = "parameter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)
    unit = db.Column(db.String(50), nullable = False)


    # 1:N parameter value
    values = db.relationship('Value',backref="parameter_back_ref")

    @classmethod
    def delete(cls, parameter_id):
        parameter = User.query.filter_by(id=parameter_id).first()
        db.session.delete(parameter)
        db.session.commit()

#user define kpi for given parameter
class Kpi(db.Model):
    __tablename__ = "kpi"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(200))
    lower_limit = db.Column(db.Float)
    upper_limit = db.Column(db.Float)

    #who define kpi
    creater = db.Column(db.Integer,db.ForeignKey('user.id'))
    #systems it is used in
    system = db.Column(db.Integer,db.ForeignKey('system.id'))

    #with parameter
    parameter_id = db.Column(db.Integer,db.ForeignKey("parameter.id"))

class Value(db.Model):
    __tablename__ = "value"

    id = db.Column(db.Integer,primary_key=True)

    value = db.Column(db.Float)

    #identification of value is given by timestamp, device, and parameter
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


    parameter = db.Column(db.Integer,db.ForeignKey('parameter.id'))
    
    
    device = db.Column(db.Integer,db.ForeignKey('device.id'))

    # setter of the value
    setter = db.Column(db.Integer,db.ForeignKey('user.id'))

def delete_system_request(user_id = None, system_id = None,db = None):
    if None in [user_id,system_id,db]:
        return
    user = User.query.filter_by(id=user_id).first()
    system=System.query.filter_by(id = system_id).first()
    system.users_requesting.remove(user)
    db.session.add(system)
    db.session.add(user)
    db.session.commit()

def parameters_of_system(system_id):
    if system_id != None:
        parameters=db.session.query(Parameter).join(Device,System.devices).filter(System.id==system_id).join(DeviceType).join(Parameter,DeviceType.parameters).all()
        return parameters

def system_all_ok(system_id):
    device_types_and_devices = db.session.query(DeviceType,Device).join(Device,System.devices).filter(System.id==system_id).join(DeviceType,Device.device_type_id == DeviceType.id).all()
    if device_types_and_devices == []:
        return "OK"
    transposed_list = list(zip(*device_types_and_devices))
    device_types, devices = transposed_list
    parameters_of_devices = []
    for device_type in device_types:
        parameters = device_type.parameters
        parameters_of_devices.append(parameters)

    values_of_devices = [Value.query.filter_by(parameter=parameter.id,device=device.id).order_by(Value.timestamp.desc()).first()  for parameters,device in zip(parameters_of_devices,devices) for parameter in parameters  ]
    kpis_of_devices = [Kpi.query.filter_by(parameter_id=parameter.id,system=system_id).all() for parameters in parameters_of_devices for parameter in parameters]
    kpi_states_of_devices = get_kpi_states(values_of_devices,kpis_of_devices)
    for kpi_states in kpi_states_of_devices:
        for state in kpi_states:
            if state == "KO":
                return "KO"
    return "OK"

def get_kpi_states(values,kpis_for_parameters):
    kpis_states_for_parameters = []
    for kpis,value in zip(kpis_for_parameters,values):
        kpis_states = []
        for kpi in kpis:
            if value == None or value.value == None:
                kpis_states.append("KO")
            elif kpi.lower_limit == None:
                if value.value <= kpi.upper_limit:
                    kpis_states.append("OK")
                else:
                    kpis_states.append("KO")
            elif kpi.upper_limit == None:
                if value.value >= kpi.lower_limit:
                    kpis_states.append("OK")
                else:
                    kpis_states.append("KO")
            else:
                if value.value <= kpi.upper_limit and value.value >= kpi.lower_limit:
                    kpis_states.append("OK")
                else:
                    kpis_states.append("KO")
        kpis_states_for_parameters.append(kpis_states)
    return kpis_states_for_parameters

def get_parameters_and_values(device_id):
    parameters_and_values = (
        db.session.query(Parameter, Value)
        .join(DeviceType, Parameter.device_types)
        .join(Device, DeviceType.devices)
        .outerjoin(Value, (Value.parameter == Parameter.id) & (Value.device == device_id))
        .filter(Device.id == device_id)
        .order_by(Parameter.id, Value.timestamp.desc())
        .distinct(Parameter.id)
        .all()
        )
    if parameters_and_values == []:
        return [],[]
    transposed_list = list(zip(*parameters_and_values))
    parameters, values = transposed_list
    return parameters,values

def get_devices_and_types(system_id):
    devices_and_types = (
        db.session.query(Device,DeviceType)
        .join(Device, DeviceType.id == Device.device_type_id)
        .filter_by(system=system_id)
        .all()
    )
    if(devices_and_types == []):
        return [],[]
    transposed_list = list(zip(*devices_and_types))
    devices, device_types = transposed_list
    return devices,device_types

def get_kpis_and_parameters(system_id):
    kpis_and_parameters = db.session.query(Parameter,Kpi).join(Parameter,Kpi.parameter_id == Parameter.id).filter(Kpi.system==system_id).all()
    if(kpis_and_parameters == []):
        return [],[]
    transposed_list = list(zip(*kpis_and_parameters))
    parameters_of_kpis, kpis = transposed_list
    return parameters_of_kpis,kpis

def values_of_device(parameter_id,device_id):
    values = (db.session.query(Value).join(DeviceType, Parameter.device_types)
               .filter(Parameter.id==parameter_id)
               .join(Device, DeviceType.devices)
                .outerjoin(Value, (Value.parameter == Parameter.id) & (Value.device == device_id))
                .filter(Device.id == device_id)
                .order_by(Parameter.id, Value.timestamp.asc())
                .all()
                )
    return values
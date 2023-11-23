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
        system = System.query.filter_by(id=system_id).first()
        devices = system.devices
        device_types_list = [DeviceType.query.filter_by(id=device.device_type_id).first() for device in devices]
        device_types_set = set(device_types_list) #throws out duplicates
        parameters = []
        for device_type in device_types_set:
            parameters.extend(device_type.parameters)
        return set(parameters)
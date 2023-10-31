from app import db
from datetime import datetime
from sqlalchemy import ForeignKeyConstraint

#TODO unique attributes and nullabel = False

user_system = db.Table('user_system',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('system_id', db.Integer, db.ForeignKey('system.id'))
                    )

class User(db.Model):
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

class System(db.Model):
    __tablename__ = "system"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),unique = True,nullable = False)
    description = db.Column(db.String(200))

    # owner/ manager of system
    system_manager = db.Column(db.Integer,db.ForeignKey('user.id'))

    # 1:N system devices
    devices = db.relationship('Device',backref="system_back_ref")

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

    #devicetype is strong entity for parameter
    parameters = db.relationship('Parameter',backref="device_type_back_ref_1",cascade='all, delete')

    #devices that are this device type
    devices = db.relationship('Device',backref="device_type_back_ref_2",cascade='all, delete')





class Parameter(db.Model):
    __tablename__ = "parameter"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)

    # device type the parameter is for
    device_type_id = db.Column(db.Integer,db.ForeignKey("device_type.id"))
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



from app.models import Parameter,DeviceType,User
from app import bcrypt

def initial_data(db):
    parameter1=Parameter(name='temperature', unit='Celsius')
    parameter2=Parameter(name='atmospheric pressure', unit='Pascal')
    parameter3=Parameter(name='humidity', unit='g/kg')

    db.session.add(parameter1)
    db.session.add(parameter2)
    db.session.add(parameter3)
    db.session.commit()

    device_type1=DeviceType(name='basic thermometer')
    device_type2=DeviceType(name='barometer')
    device_type3=DeviceType(name='super meter')
    db.session.add(device_type1)
    db.session.add(device_type2)
    db.session.add(device_type3)
    db.session.commit()

    device_type1.parameters.append(parameter1)
    device_type2.parameters.append(parameter2)
    device_type3.parameters.append(parameter1)
    device_type3.parameters.append(parameter3)
    db.session.commit()

    admin=User(username="admin",hashed_password=bcrypt.generate_password_hash("admin_heslo").decode('utf-8'),first_name="admin",last_name="admin",role="admin")
    broker=User(username="broker",hashed_password=bcrypt.generate_password_hash("broker_heslo").decode('utf-8'),first_name="broker",last_name="broker",role="broker")
    db.session.add(admin)
    db.session.add(broker)
    db.session.commit()
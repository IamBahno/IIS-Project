from app.models import Parameter,DeviceType,User
from app import bcrypt

def initial_data(db):
    parameter1=Parameter(name='temperature', unit='Celsius')
    parameter2=Parameter(name='atmospheric pressure', unit='Pascal')
    parameter3=Parameter(name='humidity', unit='g/kg')
    parameter4=Parameter(name='mass', unit='kg')
    parameter5=Parameter(name='electric current', unit='A')

    db.session.add(parameter1)
    db.session.add(parameter2)
    db.session.add(parameter3)
    db.session.add(parameter4)
    db.session.add(parameter5)
    db.session.commit()

    device_type1=DeviceType(name='Basic thermometer')
    device_type2=DeviceType(name='Barometer')
    device_type3=DeviceType(name='Super meter')
    device_type4=DeviceType(name='Ammeter')
    db.session.add(device_type1)
    db.session.add(device_type2)
    db.session.add(device_type3)
    db.session.add(device_type4)
    db.session.commit()

    device_type1.parameters.append(parameter1)
    device_type2.parameters.append(parameter2)

    device_type3.parameters.append(parameter1)
    device_type3.parameters.append(parameter3)

    device_type4.parameters.append(parameter5)
    db.session.commit()

    admin=User(username="admin",hashed_password=bcrypt.generate_password_hash("admin_heslo").decode('utf-8'),first_name="admin",last_name="admin",role="admin")
    broker=User(username="broker",hashed_password=bcrypt.generate_password_hash("broker_heslo").decode('utf-8'),first_name="broker",last_name="broker",role="broker")
    reg_user=User(username="reg_user",hashed_password=bcrypt.generate_password_hash("reg_user_heslo").decode('utf-8'),first_name="reg_user",last_name="reg_user",role="user")
    db.session.add(admin)
    db.session.add(broker)
    db.session.add(reg_user)
    db.session.commit()
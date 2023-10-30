from datetime import datetime

from app.models import User,System,Device,DeviceType, Parameter, Value, Kpi
from app import db

def test_user_update( app):
    with app.app_context():
        # Insert a user into the database
        user = User(username="xname01", hashed_password="aaaxxx333", first_name="Jmeno", last_name="Prijmeni", role="spravce")
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database and update their information
        retrieved_user = User.query.filter_by(username="xname01").first()
        assert retrieved_user is not None
        retrieved_user.username = "new_username"
        db.session.commit()

        # Retrieve the user again to verify the update
        updated_user = User.query.filter_by(username="new_username").first()
        assert updated_user is not None
        assert updated_user.username == "new_username"

def test_user_delete(client, app):
    with app.app_context():
        # Insert a user into the database
        user = User(username="xname00", hashed_password="aaaxxx333", first_name="Jmeno", last_name="Prijmeni", role="spravce")
        db.session.add(user)
        db.session.commit()

        # Delete the user from the database
        user_to_delete = User.query.filter_by(username="xname00").first()
        assert user_to_delete is not None
        db.session.delete(user_to_delete)
        db.session.commit()

        # Attempt to retrieve the user after deletion
        deleted_user = User.query.filter_by(username="xname00").first()
        assert deleted_user is None  # The user should not be found


def test_system_insert(client,app):
    with app.app_context():

        # Insert a system into the database
        system = System(name="Test System", description="System for testing")
        db.session.add(system)
        db.session.commit()

        # Retrieve the system from the database
        retrieved_system = System.query.filter_by(name="Test System").first()
        assert retrieved_system is not None
        assert retrieved_system.name == "Test System"
        assert retrieved_system.description == "System for testing"

def test_system_update(client,app):
    with app.app_context():

        # Insert a system into the database
        system = System(name="Test System", description="System for testing")
        db.session.add(system)
        db.session.commit()

        # Retrieve the system from the database and update its information
        retrieved_system = System.query.filter_by(name="Test System").first()
        assert retrieved_system is not None
        retrieved_system.name = "Updated System"
        db.session.commit()

        # Retrieve the system again to verify the update
        updated_system = System.query.filter_by(name="Updated System").first()
        assert updated_system is not None
        assert updated_system.name == "Updated System"

def test_system_delete(client,app):
    with app.app_context():

        # Insert a system into the database
        system = System(name="Test System", description="System for testing")
        db.session.add(system)
        db.session.commit()

        # Delete the system from the database
        system_to_delete = System.query.filter_by(name="Test System").first()
        assert system_to_delete is not None
        db.session.delete(system_to_delete)
        db.session.commit()

        # Attempt to retrieve the system after deletion
        deleted_system = System.query.filter_by(name="Test System").first()
        assert deleted_system is None  # The system should not be found

def test_user_manages_systems(client):
    # Create a user and two systems
    user = User(username="testuser", hashed_password="password", first_name="John", last_name="Doe", role="manager")
    system1 = System(name="System 1", description="System 1 for testing",system_manager=user)
    system2 = System(name="System 2", description="System 2 for testing",system_manager=user)

    # Add the systems to the user's managed systems
    user.managed_systems.append(system1)
    user.managed_systems.append(system2)

    # Add the user and systems to the database
    db.session.add(user)
    db.session.add(system1)
    db.session.add(system2)
    db.session.commit()

    # Retrieve the user from the database and check if they manage the systems
    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert len(retrieved_user.managed_systems) == 2
    assert system1 in retrieved_user.managed_systems
    assert system2 in retrieved_user.managed_systems

    retrieved_system = System.query.filter_by(name="System 1").first()
    assert retrieved_system is not None
    assert retrieved_system.system_manager == user.id

def test_users_use_systems(client):
    # Create users
    user1 = User(username="user1", hashed_password="password1")
    user2 = User(username="user2", hashed_password="password2")

    # Create systems
    system1 = System(name="System1", description="System for testing 1")
    system2 = System(name="System2", description="System for testing 2")

    # Add users and systems to the database
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(system1)
    db.session.add(system2)
    db.session.commit()

    # Make users use systems
    user1.used_systems.append(system1)
    user1.used_systems.append(system2)
    user2.used_systems.append(system1)

    db.session.commit()

    # Check if users are associated with the correct systems
    retrieved_user1 = User.query.filter_by(username="user1").first()
    retrieved_user2 = User.query.filter_by(username="user2").first()
    assert system1 in retrieved_user1.used_systems
    assert system2 in retrieved_user1.used_systems
    assert system1 in retrieved_user2.used_systems

    # Check if systems are associated with the correct users
    retrieved_system1 = System.query.filter_by(name="System1").first()
    retrieved_system2 = System.query.filter_by(name="System2").first()
    assert user1 in retrieved_system1.users
    assert user2 in retrieved_system1.users
    assert user1 in retrieved_system2.users

def test_device_manager(client):
    # Create a user who will be the owner/manager of the device
    manager = User(username="manager", hashed_password="managerpassword")

    # Create a device and set the owner/manager to the user
    device = Device(name="Managed Device", description="Device with manager", device_manager=manager)

    manager.devices.append(device)

    # Add the user and device to the database
    db.session.add(manager)
    db.session.add(device)
    db.session.commit()
    # Retrieve the device from the database and check if it has the correct owner/manager
    retrieved_device = Device.query.filter_by(name="Managed Device").first()
    retrieved_manager = User.query.filter_by(username="manager").first()

    assert retrieved_device is not None
    assert retrieved_device.device_manager == retrieved_manager.id

def test_device_system(client):
    # Create a system and a device and associate the device with the system
    system = System(name="Test System", description="System for testing devices")
    device = Device(name="Test Device", description="Device for testing", system=system)

    system.devices.append(device)

    # Add the system and device to the database
    db.session.add(system)
    db.session.add(device)
    db.session.commit()

    # Retrieve the device from the database and check if it is associated with the correct system
    retrieved_device = Device.query.filter_by(name="Test Device").first()
    assert retrieved_device is not None
    assert retrieved_device.system == system.id

def test_device_device_type(client):
    # Create a DeviceType
    device_type = DeviceType(name="Test Device Type")
    db.session.add(device_type)
    db.session.commit()

    # Create a Device and associate it with the DeviceType
    device = Device(name="Test Device", device_type_id=device_type.id)
    db.session.add(device)
    db.session.commit()

    retrieved_device_type = DeviceType.query.first()
    assert retrieved_device_type.devices[0].id == device.id

def test_multiple_devices_same_device_type(client):
    # Create a DeviceType
    device_type = DeviceType(name="Test Device Type")
    db.session.add(device_type)
    db.session.commit()

    # Create multiple devices with the same DeviceType
    devices = [
        Device(name=f"Device {i}", device_type_id=device_type.id)
        for i in range(1, 4)
    ]

    db.session.add_all(devices)
    db.session.commit()

    # Query all devices with the same DeviceType
    retrieved_devices = Device.query.filter_by(device_type_id=device_type.id).all()

    # Ensure the number of retrieved devices matches the number of added devices
    assert len(retrieved_devices) == len(devices)

    # Ensure all retrieved devices have the same DeviceType
    for retrieved_device in retrieved_devices:
        assert retrieved_device.device_type_id == device_type.id

def test_parameter_and_relationships(client):
    # Create a DeviceType
    device_type = DeviceType(name="Test Device Type")
    db.session.add(device_type)

    # Create a Parameter and associate it with the DeviceType
    parameter = Parameter(name="Test Parameter", device_type_id=device_type)
    device_type.parameters.append(parameter)
    db.session.add(parameter)
    db.session.commit()

    # Query the Parameter and check if it is associated with the DeviceType
    retrieved_parameter = Parameter.query.filter_by(name="Test Parameter").first()
    assert retrieved_parameter is not None
    assert retrieved_parameter.device_type_id == device_type.id


def test_create_device_type_with_device_and_values(client):
    # Create a DeviceType
    device_type = DeviceType(name="Test Device Type")

    # Create a Parameter associated with the DeviceType
    parameter = Parameter(name="Test Parameter", device_type_id=device_type)

    # Create a Device of the specified DeviceType
    device = Device(name="Test Device", device_type_id=device_type)
    
    device_type.devices.append(device)
    device_type.parameters.append(parameter)

    db.session.add(device_type)
    db.session.add(parameter)
    db.session.add(device)

    # Commit the changes to the database
    db.session.commit()

    # Create some Value records associated with the Device and Parameter at different timestamps
    timestamp1 = datetime(2023, 10, 31, 12, 0, 0)  # Replace with your desired timestamp
    timestamp2 = datetime(2023, 10, 31, 12, 30, 0)  # Replace with your desired timestamp

    value1 = Value(value=10.0, timestamp=timestamp1, parameter=parameter.id, device=device.id)
    value2 = Value(value=15.0, timestamp=timestamp2, parameter=parameter.id, device=device.id)

    db.session.add(value1)
    db.session.add(value2)
    db.session.commit()

    # Query and assert the values associated with the Device and Parameter
    retrieved_values = Value.query.filter_by(parameter=parameter.id, device=device.id).all()
    assert len(retrieved_values) == 2
    assert retrieved_values[0].value == 10.0
    assert retrieved_values[1].value == 15.0
    assert retrieved_values[0].timestamp == timestamp1
    assert retrieved_values[1].timestamp == timestamp2

def test_user_create_system_with_devices_and_kpi(client):
    # Create a user
    user = User(username="test_user", hashed_password="test_password")
    db.session.add(user)
    db.session.commit()

    # Create a device type
    device_type = DeviceType(name="Test Device Type")
    db.session.add(device_type)
    db.session.commit()

    # Create a parameter for the device type
    parameter = Parameter(name="Test Parameter", device_type_id=device_type.id)
    db.session.add(device_type)
    db.session.add(parameter)
    db.session.commit()

    # Create a system
    system = System(name="Test System", description="System for testing devices")
    system.system_manager = user.id  # Set the user as the system manager
    db.session.add(system)
    db.session.commit()

    # Create devices associated with the device type
    device1 = Device(name="Device 1", device_type_id=device_type.id, system=system.id)
    device2 = Device(name="Device 2", device_type_id=device_type.id, system=system.id)

    db.session.add(device1)
    db.session.add(device2)
    db.session.commit()

    # Create values associated with the parameter and devices
    timestamp = datetime.utcnow()
    value1 = Value(value=5.0, timestamp=timestamp, parameter=parameter.id, device=device1.id)
    value2 = Value(value=7.0, timestamp=timestamp, parameter=parameter.id, device=device2.id)
    db.session.add(value1)
    db.session.add(value2)
    db.session.commit()

    # Create a KPI for the system, device type, and parameter
    kpi = Kpi(
        description="Test KPI",
        lower_limit=4.0,
        upper_limit=6.0,
        creater=user.id,
        system=system.id,
        parameter_id=parameter.id,
    )
    db.session.add(kpi)
    db.session.commit()



    kpi_in_system = Kpi.query.filter_by(system=system.id).first()
    assert kpi_in_system != None
    kpis_device_types = DeviceType.query.filter(DeviceType.parameters.any(Parameter.id.like(kpi_in_system.parameter_id))).all()

    assert len(kpis_device_types) == 1
    kpis_device_type = kpis_device_types.pop()
    assert kpis_device_type.name == "Test Device Type"

    devices_in_system_with_device_type_as_kpi = Device.query.filter_by(system=system.id,device_type_id=kpis_device_type.id).all()
    assert len(devices_in_system_with_device_type_as_kpi) == 2


    #values of devices in parameters checked by kpi
    values_of_d1 = Value.query.filter_by(parameter=kpi_in_system.parameter_id,device=devices_in_system_with_device_type_as_kpi[0].id).all()
    values_of_d2 = Value.query.filter_by(parameter=kpi_in_system.parameter_id,device=devices_in_system_with_device_type_as_kpi[1].id).all()

    value_of_d1 = values_of_d1.pop()
    value_of_d2 = values_of_d2.pop()

    assert value_of_d1.value in [value1.value,value2.value]
    assert value_of_d2.value in [value1.value,value2.value]


    # there is value that satisfy the kpi
    assert 1 == sum(1 for value in [value_of_d1.value,value_of_d2.value] if (value >= kpi_in_system.lower_limit and value <= kpi_in_system.upper_limit))


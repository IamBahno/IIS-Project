from flask import render_template, request, Blueprint, flash, redirect, url_for
from app.models import User,System, Parameter, DeviceType, Device,Value,Kpi,delete_system_request,parameters_of_system
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

auth = Blueprint('auth', __name__)

#TODO pridat kpi do systemu, vsechny kpi projit, pokud jes aspon jedno "KO" hodit tam ko, nebo tak neco
#TODO kpi delete
#TODO nekam vypisovat veci jako kpi jmneo popis etc.
#TODO u vytvareni kpi, udelat nejak ze musi byt nastavenej aspon jedna limit, kontrolovat ze jedna mensi hodnota je oprvdu mensi, regexi na zadavani cisel
#TODO delete device v system deatilu nebo device detailu
#TODO oddelat ze v register formulari si vybiras role, (mozna pridelaat ze admin muze davat ostatnim adim role)
#TODO udelat edit ke vsemu (edit jmena osoby,kpi hodnoty, jmena device etc.....) bud predelat create page aby meli parameter create/edit 
#                       a pak to tam dost prepsat nebo zkopirovat veci z create a predelat to na edit
#TODO vypisovat vsude nejakej rozumnej header (treaba kdyz vytvaris device aby byl tam byl vypsanej system nebo tak neco )
#TODO zajisti koretkni vstupy
#TODO zajistit aby pri zadani neplatny hodnoty jako unikatni jmeno atd. nespadl program
#TODO oznacit poviny pole, aby program nepadal pri nezadani tech nepoviny atd...

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))
    if request.method == 'POST':
        username = request.values['login-username']
        password = request.values['login-password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.hashed_password,password):
            flash('Login successful', 'success')
            login_user(user)
            return redirect(url_for('auth.home'))

        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html', title='Login')

@auth.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))
    if request.method == 'POST':
#         # Registration form
        username = request.values['username']
        password = request.values['password']
        first_name = request.values['first_name']
        last_name = request.values['last_name']
        role = request.values['role']


        # Create a new User record and add it to the database
        user = User(username=username,first_name=first_name,last_name=last_name,role=role,hashed_password = bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)

        try:
            db.session.commit()
        except Exception:
            flash('User already exists', 'error')
            return '', 400

        flash('User registered successfully', 'success')

        login_user(user)

        return redirect(url_for('auth.home'))
    return render_template('register.html', title='Register')

@auth.route("/")
@auth.route("/home")
def home():
    return redirect(url_for('auth.systems'))

@auth.route("/systems",methods=['GET', 'POST'])
def systems():
    if request.method == 'POST':
        #add system button
        if 'add-system-button' in request.values:
            # The 'add-system-button' button was clicked
            # Handle the logic for creating a system here
            return redirect(url_for('auth.system_create'))
        if request.method == 'POST' and 'system-button-detail' in request.values:
            return redirect(url_for('auth.system_detail',system_id=request.values["system_id"]),code=307)
        elif request.method == 'POST' and "system-button-request" in request.values:
            # system = System.query.filter_by(id=request.values["system_id"])
            current_user.request_system.append(System.query.filter_by(id=request.values["system_id"]).first())
            db.session.add(current_user)
            db.session.commit()
        elif request.method == 'POST' and "system-button-delete" in request.values:
            system = System.query.filter_by(id=request.values["system_id"]).first()
            db.session.delete(system)
            db.session.commit()
                

    systems = [
        {"name": "System1", "id": 1, "kpis": [{"name" : "teplota", "state" : "OK"},{"name" : "vlhkost", "state" : "KO"}],"button":"detail"},
        {"name": "System2", "id" : 2,"kpis": [{"name" : "rychlost", "state" : "KO"}],"button":"pozadat o pristup"},
    ]
    systems_in_db =  System.query.all()
    for i in systems_in_db:
        system_privilages = False
        if(current_user.is_authenticated and (current_user.id == i.system_manager or i in current_user.used_systems or current_user.role == "admin" or current_user.role == "broker")):
            system_privilages = True
        if system_privilages:
            button = "detail"
        elif current_user in i.users_requesting:
            button = "request pending"
        else:
            button = "request system use"
        systems.append({"name": i.name, "id": i.id,
                        "button": button, "owner": True if system_privilages and i.system_manager == current_user.id else False})
    return render_template('systems.html',systems=systems)


@auth.route("/systems/<system_id>",methods=['GET', 'POST'])
def system_detail(system_id):
    if request.method == "GET" and "device-detail" in request.values:
        return redirect(url_for('auth.device_detail',user=request.values["user_id"],device=request.values["device_id"]))
    
    if "add-device" in request.values:
        return redirect(url_for('auth.device_create',system_id=system_id),code=307)
    elif "request-accept" in request.values:
        delete_system_request(user_id = int(request.values["request_user_id"]), system_id = int(system_id),db = db)

        user = User.query.filter_by(id=request.values["request_user_id"]).first()
        system=System.query.filter_by(id=int(system_id)).first()
        system.users.append(user)
        db.session.add(system)
        db.session.add(user)
        db.session.commit()

    elif "request-decline" in request.values:
        delete_system_request(user_id = int(request.values["request_user_id"]), system_id = int(system_id),db = db)

    system=System.query.filter_by(id = int(system_id)).first()
    devices = Device.query.filter_by(system=system.id).all()
    device_types = [DeviceType.query.filter_by(id=device.device_type_id).first()  for device in devices]
    parameters_of_devices = [device_type.parameters for  device_type in device_types]
    values_of_devices = []
    for parameters,device in zip(parameters_of_devices,devices):
        values = [Value.query.filter_by(parameter=parameter.id,device=device.id).order_by(Value.timestamp.desc()).first() for parameter in parameters]
        values_of_devices.append(values)
    
    kpis = Kpi.query.filter_by(system=system_id).all()
        #list of kpis for each parameter
    kpis_of_devices = [[Kpi.query.filter_by(parameter_id=parameter.id,system=system_id).all() for parameter in parameters] for parameters in parameters_of_devices]
    kpis_states = [get_kpi_states(values,kpis) for values,kpis in zip(values_of_devices,kpis_of_devices)]
    return render_template('system_detail.html',system=system,devices=devices,user=current_user,zip = zip,parameters = parameters_of_devices,
                           values=values_of_devices,kpis_of_devices=kpis_of_devices,kpis_states_of_devices=kpis_states, kpis=kpis)


@auth.route("/systems/<system_id>/<device_id>",methods=['GET', 'POST'])
def device_detail(system_id, device_id):
    if "add-value" in request.values:
        value_value = request.values["value"]
        try:
            value_value = int(value_value)
        except:
            value_value = float(value_value)
        value = Value(value=value_value,timestamp=request.values["time"],setter=current_user.id,device=device_id,parameter=request.values["parameter_id"])
        db.session.add(value)
        db.session.commit()
    device = Device.query.filter_by(id=device_id).first()
    device_type = DeviceType.query.filter_by(id=device.device_type_id).first()
    #list of parameters
    parameters = device_type.parameters
    #list of values
    values = [Value.query.filter_by(parameter=parameter.id,device=device.id).order_by(Value.timestamp.desc()).first() for parameter in parameters]
    #list of kpis for each parameter
    kpis = [Kpi.query.filter_by(parameter_id=parameter.id,system=system_id).all() for parameter in parameters]
    #list of kpi states for parameters
    kpi_states = get_kpi_states(values,kpis)
    return render_template('device_detail.html', device_id=int(device_id), system_id=int(system_id),user=current_user,values=values,
                           parameters=parameters,kpis=kpis,kpi_parameters_states=kpi_states,default_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),zip=zip)
    
@auth.route("/systems/<system_id>/create",methods=['GET', 'POST'])
def device_create(system_id):
    if "create-device" in request.values:
        device = Device(name = request.values["device-name"],description=request.values["device-description"],system=int(system_id),device_manager=current_user.id,device_type_id=request.values.get("device-type"))
        db.session.add(device)
        db.session.commit()
        return redirect(url_for('auth.system_detail',system_id=int(system_id)),code=307)
    device_types = DeviceType.query.all()
    parameters_of_device_types = {}
    for device_type in device_types:
        parameter_names = []
        for parameter in device_type.parameters:
            parameter_names.append(parameter.name)
        parameters_of_device_types[device_type.name] = parameter_names
    return render_template('device_create.html',device_types=device_types,parameters=parameters_of_device_types,system_id=int(system_id))


@auth.route("/systems/create",methods=['GET', 'POST'])
def system_create():
    if request.method == 'POST':
        #add system button
        if 'create-system' in request.values:
            if not current_user.is_authenticated:
                flash("Log-in first")
                print("Log-in first")
            system_name = request.values['system-name']
            system_description = request.values['system-description']
            if(System.query.filter_by(name=system_name).first() != None):
                print("System with that name already exists")
            #zjistit jestli uz neni system toho jmena
            system = System(name=system_name,description=system_description,system_manager=current_user.id)
            db.session.add(system)
            db.session.commit()
            print("system created")
            return redirect(url_for('auth.systems'))
    return render_template('system_create.html')

@auth.route("/systems/<system_id>/kpi/create",methods=['GET','POST'])
def kpi_create(system_id):
    if "add-kpi-form" in request.values:
        parameters = parameters_of_system(system_id)
        return render_template('kpi_create.html',parameters=parameters)
    elif "create-kpi" in request.values:
        lower_limit = float(request.values["lower_limit"]) if request.values["lower_limit"] != "" else None
        upper_limit = float(request.values["upper_limit"]) if request.values["upper_limit"] != "" else None
        kpi = Kpi(name=request.values["kpi_name"],description=request.values["kpi_description"],system=system_id,
                  parameter_id=int(request.values['parameter']),lower_limit=lower_limit,upper_limit=upper_limit,creater=current_user.id)
        db.session.add(kpi)
        db.session.commit()
        return redirect(f'/systems/{system_id}')

    return "<p>nevadi</p>"

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

# @auth.route("/test",methods=['GET', 'POST'])
# @login_required
# def test():
#     pass
from flask import render_template, request, Blueprint, flash, redirect, url_for, abort
from app.models import User,System, Parameter, DeviceType, Device,Value,Kpi,delete_system_request,parameters_of_system,system_all_ok,get_kpi_states,get_kpis_and_parameters,get_parameters_and_values,get_devices_and_types
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from is_safe_url import is_safe_url
from app.forms import RegisterForm,KPIEditForm,LoginForm,SystemEditForm,DeviceEditForm,DeviceTypeEditForm

auth = Blueprint('auth', __name__)

#TODO sipku zpet
#TODO admin manage Users, (delete, change password ?)
#TODO create parameter device_type
#TODO kdyz nejse smazat parameter neco vypsat
#TODO device_type edit
#TODO device detail styles
#TODO device detail form rewrite
#TODO otestovat co se stane kdy admin smaze device_type kterej je v nejakym systemu
#TODO udelat edit ke vsemu (edit jmena osoby,kpi hodnoty, jmena device etc.....) bud predelat create page aby meli parameter create/edit 
#                       a pak to tam dost prepsat nebo zkopirovat veci z create a predelat to na edit
#TODO vypisovat vsude nejakej rozumnej header (treaba kdyz vytvaris device aby byl tam byl vypsanej system nebo tak neco )
#TODO zajisti koretkni vstupy

@auth.route("/login/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        flash('Login successful', 'success')
        login_user(user)
        next = request.args.get('next')
        if next == "" or next == None or not is_safe_url(next, request.host):
            return redirect(url_for('auth.home'))

        return redirect(next)
    return render_template('login.html', title='Login', form=form)

@auth.route("/logout/", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))


    form = RegisterForm()
    if form.validate_on_submit():
#         # Registration form

        # Create a new User record and add it to the database
        user = User(username=form.username.data,first_name=form.first_name.data,last_name=form.last_name.data,role="user",hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('auth.home'))

    return render_template('register.html', title='Register', form=form)

@auth.route("/")
@auth.route("/home")
def home():
    return redirect(url_for('auth.systems'))

@auth.route("/systems/",methods=['GET', 'POST'])
def systems():
    systems = []
    systems_in_db =  System.query.all()
    for i in systems_in_db:
        system_privilages = False
        if(current_user.is_authenticated and (current_user.id == i.system_manager or i in current_user.used_systems or current_user.role == "admin" or current_user.role == "broker")):
            system_privilages = True
        if system_privilages:
            button = "Detail"
        elif current_user in i.users_requesting:
            button = "Request pending"
        else:
            button = "Request system use"
        system_state = system_all_ok(i.id)
        systems.append({"name": i.name, "id": i.id,
                        "button": button, "state":system_state,"owner": True if system_privilages and i.system_manager == current_user.id else False})

    return render_template('systems.html',systems=systems, title="Systems")

@auth.route("/systems/<int:system_id>/delete/",methods=['GET', 'POST'])
@login_required
def system_delete(system_id):
    system = System.query.get_or_404(system_id)

    if current_user.role != "admin" and current_user.id != system.system_manager:
        abort(403)

    db.session.delete(system)
    db.session.commit()
    return redirect(url_for('auth.systems'))

@auth.route("/systems/<int:system_id>/",methods=['GET', 'POST'])
@login_required
def system_detail(system_id):
    system=System.query.get_or_404(system_id)
    if system not in current_user.used_systems and current_user.id != system.system_manager and current_user.role != "admin":
        abort(403)

    title = system.name

    devices,device_types = get_devices_and_types(system_id)


    parameters_of_devices,values_of_devices = [],[]
    for device in devices:
        parameters,values = get_parameters_and_values(device.id)
        parameters_of_devices.append(parameters)
        values_of_devices.append(values)


    parameters_of_kpis, kpis = get_kpis_and_parameters(system.id)


    #list of kpis for each parameter
    kpis_of_devices = [[Kpi.query.filter_by(parameter_id=parameter.id,system=system_id).all() for parameter in parameters] for parameters in parameters_of_devices]
    kpis_states = [get_kpi_states(values,kpis) for values,kpis in zip(values_of_devices,kpis_of_devices)]
    return render_template('system_detail.html',system=system,devices=devices,user=current_user,zip = zip,parameters = parameters_of_devices,
                           values=values_of_devices,kpis_of_devices=kpis_of_devices,kpis_states_of_devices=kpis_states, kpis=kpis, parameters_of_kpis=parameters_of_kpis, title=title)


@auth.route("/systems/<int:system_id>/request/", methods=['GET', 'POST'])
@login_required
def system_request_access(system_id):
    system = System.query.get_or_404(system_id)
    
    if current_user in system.users or current_user.role == "admin":
        return redirect(url_for('auth.system_detail',system_id=system_id))

    if current_user in system.users_requesting:
        return redirect(url_for('auth.systems'))

    system.users_requesting.append(current_user)

    db.session.commit()

    return redirect(url_for('auth.systems'))

@auth.route("/systems/<int:system_id>/requests/<int:user_id>/accept/", methods=['GET', 'POST'])
@login_required
def system_accept_request(system_id, user_id):
    system = System.query.get_or_404(system_id)
    user = User.query.get_or_404(user_id)

    if current_user.id != system.system_manager and current_user.role != "admin":
        abort(403)
    
    if user in system.users or user not in system.users_requesting:
        return redirect(url_for('auth.system_detail',system_id=system_id))

    delete_system_request(user_id = user_id, system_id = system_id,db = db)
    user.used_systems.append(system)

    db.session.commit()

    return redirect(url_for('auth.system_detail',system_id=system_id))

@auth.route("/systems/<int:system_id>/requests/<int:user_id>/reject/", methods=['GET', 'POST'])
@login_required
def system_reject_request(system_id, user_id):
    system = System.query.get_or_404(system_id)
    user = User.query.get_or_404(user_id)

    if current_user.id != system.system_manager and current_user.role != "admin":
        abort(403)
    
    if user in system.users or user not in system.users_requesting:
        return redirect(url_for('auth.system_detail',system_id=system_id))

    delete_system_request(user_id = user_id, system_id = system_id,db = db)

    db.session.commit()

    return redirect(url_for('auth.system_detail',system_id=system_id))

@auth.route("/systems/<int:system_id>/requests/<int:user_id>/revoke/", methods=['GET', 'POST'])
@login_required
def system_revoke_request(system_id, user_id):
    system = System.query.get_or_404(system_id)
    user = User.query.get_or_404(user_id)

    if current_user.id != system.system_manager and current_user.role != "admin" and current_user.id != user_id:
        abort(403)
    
    if user in system.users:
        user.used_systems.remove(system)
        db.session.commit()

    if current_user.id == user_id:
        return redirect(url_for('auth.home'))

    return redirect(url_for('auth.system_detail',system_id=system_id))

@auth.route("/systems/<int:system_id>/kpi/<int:kpi_id>/delete/",methods=['GET', 'POST'])
@login_required
def kpi_delete(system_id, kpi_id):
    system = System.query.get_or_404(system_id)

    if current_user.role != "admin" and current_user.id != system.system_manager:
        abort(403)

    kpi = Kpi.query.get_or_404(kpi_id)
    db.session.delete(kpi)
    db.session.commit()
    return redirect(url_for('auth.system_detail',system_id=system_id))

@auth.route("/systems/<int:system_id>/devices/<int:device_id>/delete/",methods=['GET', 'POST'])
@login_required
def device_delete(system_id, device_id):
    system = System.query.get_or_404(system_id)

    if current_user.role != "admin" and current_user.id != system.system_manager:
        abort(403)

    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return redirect(url_for('auth.system_detail',system_id=system_id))


@auth.route("/systems/<int:system_id>/devices/<int:device_id>/",methods=['GET', 'POST'])
@login_required
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
    device = Device.query.get_or_404(device_id)
    title = device.name

    parameters,values = get_parameters_and_values(device.id)

    #list of kpis for each parameter
    kpis = [Kpi.query.filter_by(parameter_id=parameter.id,system=system_id).all() for parameter in parameters]
    #list of kpi states for parameters
    kpi_states = get_kpi_states(values,kpis)
    return render_template('device_detail.html', device_id=int(device_id), system_id=system_id,user=current_user,values=values,
                           parameters=parameters,kpis=kpis,kpi_parameters_states=kpi_states,default_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),zip=zip, title=title)
    
@auth.route("/systems/<int:system_id>/devices/create/",methods=['GET', 'POST'])
@auth.route("/systems/<int:system_id>/devices/<int:device_id>/edit/",methods=['GET', 'POST'])
def device_create(system_id, device_id = None):
    form = DeviceEditForm()
    device_types = DeviceType.query.all()
    form.device_type.choices = [(d.id, f"{d.name} ({', '.join(p.name for p in d.parameters)})") for d in device_types]
    title = "Create device"

    system = System.query.get_or_404(system_id)

    if current_user.role != "admin" and current_user.id != system.system_manager:
        abort(403)

    if device_id:
        device = Device.query.get_or_404(device_id)
        form.device_type.validate_choice = False
        form.device_type.validators = []
        form.device_type.flags.disabled = True  

    if form.validate_on_submit():
        if not device_id:
            device = Device(name = form.device_name.data,description=form.device_description.data, system=system_id,device_manager=current_user.id,device_type_id=form.device_type.data)
            db.session.add(device)
        else:
            device.name = form.device_name.data
            device.description = form.device_description.data

        db.session.commit()
        return redirect(url_for('auth.system_detail',system_id=system_id))

    elif device_id and not form.is_submitted():
        form.device_name.data = device.name
        form.device_description.data = device.description
        form.device_type.data = device.device_type_id
        title = f"Edit device {device_id}"


    return render_template('device_create.html', form=form, title=title)


@auth.route("/systems/create/",methods=['GET', 'POST'])
@auth.route("/systems/<int:system_id>/edit/",methods=['GET', 'POST'])
@login_required
def system_create(system_id = None):
    form = SystemEditForm()
    title = "Create system"

    if system_id:
        system = System.query.get_or_404(system_id)

        if current_user.role != "admin" and current_user.id != system.system_manager:
            abort(403)

    if form.validate_on_submit():
        #add system button
        if not system_id:
            system = System(name=form.system_name.data,description=form.system_description.data,system_manager=current_user.id)
            db.session.add(system)
        else:
            #todo check
            system.name = form.system_name.data
            system.description = form.system_description.data

        db.session.commit()

        return redirect(url_for('auth.system_detail', system_id = system.id))
    elif system_id and not form.is_submitted():
        form.system_name_edit.data = system.name
        form.system_name.data = system.name
        form.system_description.data = system.description
        title = f"Edit system {system_id}"

    return render_template('system_create.html', form=form, title=title)

@auth.route("/systems/<int:system_id>/kpi/create/",methods=['GET','POST'])
@auth.route("/systems/<int:system_id>/kpi/<int:kpi_id>/edit/",methods=['GET', 'POST'])
@login_required
def kpi_create(system_id, kpi_id = None):
    form = KPIEditForm()
    parameters = parameters_of_system(system_id)
    form.parameter.choices = [(p.id, p.name) for p in parameters]
    title = "Create KPI"

    system = System.query.get_or_404(system_id)

    if current_user.role != "admin" and current_user.id != system.system_manager:
        abort(403)

    if kpi_id:
        kpi = Kpi.query.get_or_404(kpi_id)

    if form.validate_on_submit():
        if not kpi_id:
            kpi = Kpi(name=form.kpi_name.data,description=form.kpi_description.data,system=system_id,
                  parameter_id=form.parameter.data,lower_limit=form.lower_limit.data,upper_limit=form.upper_limit.data,creater=current_user.id)
            db.session.add(kpi)
        else:
            kpi.name = form.kpi_name.data
            kpi.description = form.kpi_description.data
            kpi.parameter = form.parameter.data
            kpi.lower_limit = form.lower_limit.data
            kpi.upper_limit = form.upper_limit.data

        db.session.commit()

        return redirect(f'/systems/{system_id}/')

    elif kpi_id and not form.is_submitted():
        form.kpi_name.data = kpi.name
        form.kpi_description.data = kpi.description
        form.parameter.data = kpi.parameter_id
        form.lower_limit.data = kpi.lower_limit
        form.upper_limit.data = kpi.upper_limit
        title = f"Edit KPI {kpi_id}"

    return render_template('kpi_create.html', form=form, title=title)

@auth.route("/devices_&_parameters/",methods=['GET','POST'])
@login_required
def manage_devices_and_parameters():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)
    title = "Device and parameter manager"
    device_types = DeviceType.query.all()
    parameters = Parameter.query.all()
    return render_template('devicetypes_parameters.html', device_types=device_types,parameters = parameters, title=title)

@auth.route("/device_types/create",methods=['GET','POST'])
@login_required
def create_device_type():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)
    # TODO create
    return redirect(url_for('auth.manage_devices_and_parameters'))

@auth.route("/device_types/<int:device_type_id>/delete",methods=['GET','POST'])
@login_required
def delete_device_type(device_type_id):
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)
    device_type = DeviceType.query.get_or_404(device_type_id)
    db.session.delete(device_type)
    db.session.commit()
    return redirect(url_for('auth.manage_devices_and_parameters'))

@auth.route("/parameters/create",methods=['GET','POST'])
@login_required
def create_parameter():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)
    # TODO create
    return redirect(url_for('auth.manage_devices_and_parameters'))

@auth.route("/parameters/<int:parameter_id>/delete",methods=['GET','POST'])
@login_required
def delete_parameter(parameter_id):
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)
    parameter = Parameter.query.get_or_404(parameter_id)
    if (parameter.device_types != []):
        return redirect(url_for("auth.manage_devices_and_parameters"),code=307)
    db.session.delete(parameter)
    db.session.commit()
    return redirect(url_for('auth.manage_devices_and_parameters'))

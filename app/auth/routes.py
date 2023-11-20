from flask import render_template, request, Blueprint, flash, redirect, url_for
from app.models import User,System, Parameter
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)


logged_user = None

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))
    # Login form (you can handle this part)
    # Extract login form data and perform login logic here
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.hashed_password,password):
            flash('Login successful', 'success')
            login_user(user)
            return redirect(url_for('auth.home'))

                # Redirect to a profile page or wherever you want
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html', title='Login')

@auth.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

#TODO unique username constaint
@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(auth.home))
    if request.method == 'POST':
#         # Registration form
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']


        # Create a new User record and add it to the database
        user = User(username=username,first_name=first_name,last_name=last_name,role=role,hashed_password = bcrypt.generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        flash('User registered successfully', 'success')

        login_user(user)

        return redirect(url_for('auth.home'))
    return render_template('register.html', title='Register')

@auth.route("/")
@auth.route("/home")
def home():
    return redirect(url_for('auth.systems'))

# TODO pridat device do systemu, pridat kpi
#TODO request detail
#TODO pridat ze detail bude mit i user kterej usuje
@auth.route("/systems",methods=['GET', 'POST'])
def systems():
    if request.method == 'POST':
        #add system button
        if 'add-system-button' in request.form:
            # The 'add-system-button' button was clicked
            # Handle the logic for creating a system here
            return redirect(url_for('auth.system_create'))
        if request.method == 'POST' and 'system-button-detail' in request.form:
            return redirect(url_for('auth.system_detail',system_id=request.form["system_id"]),code=307)
        elif request.method == 'POST' and "system-button-request" in request.form:
            return redirect(url_for('auth.system_request'))
                


    systems = [
        {"name": "System1", "id": 1, "kpis": [{"name" : "teplota", "state" : "OK"},{"name" : "vlhkost", "state" : "KO"}],"button":"detail"},
        {"name": "System2", "id" : 2,"kpis": [{"name" : "rychlost", "state" : "KO"}],"button":"pozadat o pristup"},
    ]
    systems_in_db =  System.query.all()
    # print(systems_in_db)
    for i in systems_in_db:
        system_privilages = False
        if(current_user.is_authenticated and current_user.id == i.system_manager):
            system_privilages = True
        systems.append({"name": i.name, "id": i.id,"button": "detail" if system_privilages else "pozadat o pristup"})
    return render_template('systems.html',systems=systems)

@auth.route("/systems/detail",methods=['GET', 'POST'])
def system_detail():
    if "system_id" in request.form:
        if "add-device" in request.form:
            return redirect(url_for('auth.device_create',system_id=request.form["system_id"]),code=307)
        system=System.query.filter_by(id = int(request.form["system_id"])).first()
        return render_template('system_detail.html',system=system)
    return "<p>ahoj</p>"

@auth.route("/device/create",methods=['GET', 'POST'])
def device_create():
    return render_template('device_create.html')

@auth.route("/systems/system_request",methods=['GET', 'POST'])
def system_request():
    return render_template('')

@auth.route("/systems/create",methods=['GET', 'POST'])
def system_create():
    if request.method == 'POST':
        #add system button
        if 'create-system' in request.form:
            if not current_user.is_authenticated:
                flash("Log-in first")
                print("Log-in first")
            system_name = request.form['system-name']
            system_description = request.form['system-description']
            if(System.query.filter_by(name=system_name).first() != None):
                print("System with that name already exists")
            #zjistit jestli uz neni system toho jmena
            system = System(name=system_name,description=system_description,system_manager=current_user.id)
            db.session.add(system)
            db.session.commit()
            print("system created")
            return redirect(url_for('auth.systems'))
    return render_template('system_create.html')

# @auth.route("/test",methods=['GET', 'POST'])
# @login_required
# def test():
#     pass
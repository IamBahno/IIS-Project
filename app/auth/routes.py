from flask import render_template, request, Blueprint, flash, redirect, url_for
from app.models import User,System
from app import db, bcrypt
from flask_login import login_user

auth = Blueprint('auth', __name__)


# @auth.route("/auth", methods=['GET', 'POST'])
# def register():
#     if 'register' in request.form:
#         # Registration form
#         username = request.form['username']
#         password = request.form['password']
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         role = request.form['role']


#         # Create a new User record and add it to the database
#         user = User(username=username,first_name=first_name,last_name=last_name,role=role,hashed_password = bcrypt.generate_password_hash(password))
#         db.session.add(user)
#         db.session.commit()

#         flash('User registered successfully', 'success')
#     elif 'login' in request.form:
#         # Login form (you can handle this part)
#         # Extract login form data and perform login logic here
#         username = request.form['login-username']
#         password = request.form['login-password']
#         user = User.query.filter_by(username=username).first()
#         if user and bcrypt.check_password_hash(user.hashed_password,password):
#             flash('Login successful', 'success')
#                 # Redirect to a profile page or wherever you want
#         else:
#             flash('Login failed. Please check your credentials.', 'danger')

#     users = User.query.all()

#     # Prepare the data for display
#     user_data = []
#     for user in users:
#         user_data.append(f"ID: {user.id}, Username: {user.username}, Last name: {user.last_name}, Password hashed: {user.hashed_password}")

#     return render_template('index.html', user_data=user_data)

logged_user = None

@auth.route("/login", methods=['GET', 'POST'])
def login():
    # Login form (you can handle this part)
    # Extract login form data and perform login logic here
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.hashed_password,password):
            flash('Login successful', 'success')
            login_user(user)
            logged_user = username
            return redirect(url_for('auth.home'))

                # Redirect to a profile page or wherever you want
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html', title='Login')

@auth.route("/register", methods=['GET', 'POST'])
def register():
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
        if 'add-system-button' in request.form:
            # The 'add-system-button' button was clicked
            # Handle the logic for creating a system here
            return redirect(url_for('auth.system_create'))


    systems = [
        {"name": "System1", "id": 1, "kpis": [{"name" : "teplota", "state" : "OK"},{"name" : "vlhkost", "state" : "KO"}],"button":"detail"},
        {"name": "System2", "id" : 2,"kpis": [{"name" : "rychlost", "state" : "KO"}],"button":"pozadat o pristup"},
    ]
    return render_template('systems.html',systems=systems)

@auth.route("/systems/create",methods=['GET', 'POST'])
def system_create():
    if request.method == 'POST':
        #add system button
        if 'create-system' in request.form:
            system_name = request.form['system-name']
            system_description = request.form['system-description']
            if(System.query.filter_by(name=system_name).first() != None):
                print("System with that name already exists")
            #zjistim lognutyho usera
            # a vytvorim novej system
            #redirectnu zpet
    return render_template('system_create.html')
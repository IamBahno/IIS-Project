from flask import render_template, request, Blueprint, flash, redirect, url_for
from app.models import User
from app import db, bcrypt


auth = Blueprint('auth', __name__)


@auth.route("/", methods=['GET', 'POST'])
def home():
    if 'register' in request.form:
        # Registration form
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
    elif 'login' in request.form:
        # Login form (you can handle this part)
        # Extract login form data and perform login logic here
        username = request.form['login-username']
        password = request.form['login-password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.hashed_password,password):
            flash('Login successful', 'success')
                # Redirect to a profile page or wherever you want
        else:
            flash('Login failed. Please check your credentials.', 'danger')

    users = User.query.all()

    # Prepare the data for display
    user_data = []
    for user in users:
        user_data.append(f"ID: {user.id}, Username: {user.username}, Last name: {user.last_name}, Password hashed: {user.hashed_password}")

    return render_template('index.html', user_data=user_data)

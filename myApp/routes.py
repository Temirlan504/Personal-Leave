import random
from flask import render_template, flash, redirect, url_for
from myApp import app, bcrypt, db
from datetime import datetime
from myApp.forms import AddUserForm, LoginForm
from myApp.models import User
from flask_login import login_required, login_user, logout_user, current_user
from myApp.utils.email_utils import generate_unique_email

# Define the homepage routes
@app.route('/')
@login_required
def home():
    greeting = get_greeting()  # e.g. "morning", "afternoon", etc.
    return render_template("homepage.html",
        greeting=greeting,
        user=current_user
    )

def get_greeting():
    try:
        current_hour = datetime.now().hour
        if 0 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 18:
            return "Good afternoon"
        elif 18 <= current_hour <= 23:
            return "Good evening"
        else:
            return "Hello"  # Fallback for unexpected hour values
    except Exception:
        return "Hello"  # Fallback for any error (e.g. datetime failure)
    

# Define the login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your email and password', 'danger')
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('login'))


# Define profile page routes
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id != user.id:
        return redirect(url_for('home'))
    return render_template("profile_page.html", user=user)


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    form = AddUserForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=generate_unique_email(form.first_name.data, form.last_name.data),
            phone=form.phone.data.strip() if form.phone.data else None,  # Ensure phone is None if empty
            password=hashed_pw,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('add_user'))
    return render_template('admin_add_user.html', form=form)

import random
from flask import render_template, flash, redirect, url_for
from myApp import app, bcrypt, db
from datetime import datetime
from myApp.forms import AddUserForm, EditProfileForm, LoginForm
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
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id != user.id and current_user.role != 'admin':
        flash('You do not have permission to view this profile.', 'danger')
        return redirect(url_for('home'))
    
    form = EditProfileForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', user_id=user.id))
    
    dummy_requests = [
        {
            "type": "Vacation",
            "start_date": "May 1, 2023",
            "end_date": "May 10, 2023",
            "pay_requested": "Yes",
            "date_submitted": "April 15, 2023",
            "status": "approved"
        },
        {
            "type": "PEL",
            "start_date": "May 12, 2023",
            "end_date": "May 16, 2023",
            "pay_requested": "No",
            "date_submitted": "April 15, 2023",
            "status": "pending"
        },
        {
            "type": "PEL",
            "start_date": "May 21, 2023",
            "end_date": "May 25, 2023",
            "pay_requested": "Yes",
            "date_submitted": "April 15, 2023",
            "status": "approved"
        },
        {
            "type": "Vacation",
            "start_date": "May 26, 2023",
            "end_date": "June 5, 2023",
            "pay_requested": "Yes",
            "date_submitted": "April 15, 2023",
            "status": "declined"
        }
    ]

    return render_template("profile_page.html", user=user, form=form, dummy_requests=dummy_requests)


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
    
    users = User.query.all()
    return render_template('admin_add_user.html', form=form, users=users)

import secrets
from flask import render_template, flash, redirect, url_for
from myApp import app, bcrypt, db
from myApp.forms import AddUserForm, LoginForm, RequestForm
from myApp.models import User, PEL, Vacation
from flask_login import login_required, login_user, logout_user, current_user
from myApp.utils.email_utils import generate_unique_email
from myApp.utils.greeting_utils import get_greeting

# Define the homepage routes
@app.route('/')
@login_required
def home():
    greeting = get_greeting()  # e.g. "morning", "afternoon", etc.
    users = User.query.all()  # Fetch all users from the database
    return render_template("homepage.html",
        greeting=greeting,
        user=current_user,
        users=users
    )
    

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
    
    # Get actual PEL and Vacation requests from the DB
    vacation_requests = Vacation.query.filter_by(user_id=user.id).all()
    pel_requests = PEL.query.filter_by(user_id=user.id).all()

    # Combine and sort them by submission or start date (optional)
    all_requests = vacation_requests + pel_requests
    all_requests.sort(key=lambda r: r.start_date)

    return render_template("profile_page.html", user=user, all_requests=all_requests)


# Admin routes for adding and managing users
@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    form = AddUserForm()
    if form.validate_on_submit():
        random_password = secrets.token_urlsafe(16)  # Generate a random password
        hashed_pw = bcrypt.generate_password_hash(random_password).decode('utf-8')
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=generate_unique_email(form.first_name.data, form.last_name.data),
            phone=form.phone.data.strip() if form.phone.data else None,  # Ensure phone is None if empty
            password=hashed_pw,
            role=form.role.data,
            date_joined=form.date_joined.data,
            base_salary=form.base_salary.data if form.base_salary.data else 1.0  # Default to 1.0 if not provided
        )
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('add_user'))
    
    users = User.query.all()
    return render_template('admin_add_user.html', form=form, users=users)


# Define routes for vacation/pel requests
@app.route('/pel-request', methods=['GET', 'POST'])
@login_required
def pel_request():
    form = RequestForm()
    if form.validate_on_submit():
        pel = PEL(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid=(form.is_paid.data == 'yes' if form.is_paid.data else False)  # Convert to boolean
        )
        db.session.add(pel)
        db.session.commit()
        flash('PEL request submitted.')
        return redirect(url_for('profile'))
    return render_template('pel_form.html', form=form)

@app.route('/vacation-request', methods=['GET', 'POST'])
@login_required
def vacation_request():
    form = RequestForm()
    if form.validate_on_submit():
        vacation = Vacation(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid=(form.is_paid.data == 'yes' if form.is_paid.data else False)  # Convert to boolean
        )
        db.session.add(vacation)
        db.session.commit()
        flash('Vacation request submitted.')
        return redirect(url_for('profile'))
    return render_template('vacation_form.html', form=form)
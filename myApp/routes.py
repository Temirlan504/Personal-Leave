import secrets
from flask import abort, render_template, flash, redirect, url_for, request
from myApp import app, bcrypt, db, mail
from myApp.forms import (
    AddUserForm, LoginForm, RequestForm,
    RequestResetForm, ResetPasswordForm
)
from myApp.models import User, PEL, Vacation
from flask_login import login_required, login_user, logout_user, current_user
from myApp.utils.convert_dollars import convert_dollars_to_days_hours
from myApp.utils.email_utils import generate_unique_email
from myApp.utils.greeting_utils import get_greeting
from myApp.utils.send_reset_email import send_reset_email
from datetime import date

@app.route('/')
@login_required
def home():
    greeting = get_greeting()
    
    if current_user.role in ['admin', 'hr']:
        page = request.args.get('page', 1, type=int)
        vacation_requests = Vacation.query.all()
        pel_requests = PEL.query.all()
        for p in pel_requests:
            p.type = 'pel'
        for v in vacation_requests:
            v.type = 'vacation'
        all_requests = vacation_requests + pel_requests
        all_requests.sort(key=lambda r: r.created_at, reverse=True)

        # ✅ Slice the list manually for pagination
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page
        paginated_requests = all_requests[start:end]

        return render_template("homepage.html",
            greeting=greeting,
            user=current_user,
            all_requests=paginated_requests,
            page=page
        )

    # For normal users
    vacation_requests = Vacation.query.filter_by(user_id=current_user.id).all()
    pel_requests = PEL.query.filter_by(user_id=current_user.id).all()
    return render_template("homepage.html",
        greeting=greeting,
        user=current_user,
        vacation_requests=vacation_requests,
        pel_requests=pel_requests
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

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template("reset_request.html", form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template("reset_token.html", form=form)


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

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of requests per page
    total = len(all_requests)
    paginated_requests = all_requests[(page - 1) * per_page: page * per_page]

    return render_template(
        "profile_page.html", user=user, all_requests=all_requests,
        paginated_requests=paginated_requests, total=total,
        page=page, per_page=per_page
    )


# Admin routes
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
@app.route('/pel_request', methods=['GET', 'POST'])
@login_required
def pel_request():
    form = RequestForm()
    pending_pel = PEL.query.filter_by(user_id=current_user.id).filter(PEL.status == 'pending').first()
    if pending_pel:
        flash("You already have a pending PEL request. Please wait for it to be processed.", "warning")
        return redirect(url_for('profile', user_id=current_user.id))
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        is_paid = form.is_paid.data
        requested_days = (end_date - start_date).days + 1

        # Check limits using method in User model
        allowed, message = current_user.can_take_pel(is_paid, requested_days)
        if not allowed:
            flash(message, 'danger')
            return redirect(url_for('pel_request'))
        elif message:
            flash(message, 'info')  # This means allowed == True but there's an FYI
        
        pel = PEL(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid=(form.is_paid.data == 'yes' if form.is_paid.data else False)
        )
        db.session.add(pel)
        db.session.commit()
        flash('PEL request submitted.')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('pel_form.html', form=form, date=date)

@app.route('/vacation_request', methods=['GET', 'POST'])
@login_required
def vacation_request():
    form = RequestForm()
    # Check for existing pending Vacation request
    pending_vacation = Vacation.query.filter_by(user_id=current_user.id).filter(Vacation.status == 'pending').first()
    if pending_vacation:
        flash("You already have a pending vacation request. Please wait for it to be processed.", "warning")
        return redirect(url_for('profile', user_id=current_user.id))
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        is_paid = form.is_paid.data
        requested_days = (end_date - start_date).days + 1
        available_days = current_user.get_available_vacation_days()

        # Check for reverse or negative dates
        if start_date > end_date:
            flash("Start date cannot be after end date.", "danger")
            return redirect(url_for('vacation_request'))

        if is_paid and requested_days > available_days:
            flash(f"You only have {available_days} paid vacation days left.", "danger")
            return redirect(url_for('vacation_request'))

        # For info: how much would they get paid
        if is_paid:
            accrued_dollars = current_user.get_total_vacation_accrued_dollars()
            daily_pay = current_user.base_salary / 260
            requested_cost = requested_days * daily_pay

            if requested_cost > accrued_dollars:
                flash(f"⚠ You'll only be paid for up to ${accrued_dollars:.2f} "
                      f"(approx. {convert_dollars_to_days_hours(current_user, accrued_dollars)[0]}d "
                      f"{convert_dollars_to_days_hours(current_user, accrued_dollars)[1]}h).", "info")
            else:
                flash(f"You will be paid ${requested_cost:.2f} "
                      f"(approx. {requested_days} days).", "info")
                
        vacation = Vacation(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid=(form.is_paid.data == 'yes' if form.is_paid.data else False)
        )
        db.session.add(vacation)
        db.session.commit()
        flash('Vacation request submitted.')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('vacation_form.html', form=form, date=date)

@app.route('/request_detail/<string:request_type>/<int:request_id>', methods=['GET', 'POST'])
@login_required
def request_detail(request_type, request_id):
    request_obj = PEL.query.get(request_id) if request_type == 'pel' else Vacation.query.get(request_id)
    if not request_obj:
        flash("Request not found.", "danger")
        return redirect(url_for('home'))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "approve_admin" and current_user.role == "admin":
            request_obj.admin_approved = True
        elif action == "approve_hr" and current_user.role == "hr":
            request_obj.hr_approved = True
        elif action == "decline":
            request_obj.status = "declined"

        # Final approval
        if request_obj.admin_approved and request_obj.hr_approved:
            request_obj.status = "approved"

        db.session.commit()
        return redirect(url_for("request_detail", request_type=request_type, request_id=request_id))

    return render_template('request_detail.html', req=request_obj)
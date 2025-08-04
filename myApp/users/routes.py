from math import ceil
import bcrypt
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from myApp import db, bcrypt
from myApp.users.forms import LoginForm, RequestResetForm, ResetPasswordForm
from myApp.models import User, Vacation, PEL
from myApp.users.utils import send_reset_email

users_bp = Blueprint('users', __name__)


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check your email and password', 'danger')
    return render_template("login.html", form=form)

@users_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('users.login'))

@users_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", form=form)

@users_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", form=form)

@users_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id != user.id and current_user.role != 'admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.home'))

    # Get actual PEL and Vacation requests from the DB
    vacation_requests = Vacation.query.filter_by(user_id=user.id).all()
    pel_requests = PEL.query.filter_by(user_id=user.id).all()
    for p in pel_requests:
        p.type = 'pel'
    for v in vacation_requests:
        v.type = 'vacation'

    # Combine and sort them by submission or start date (optional)
    all_requests = vacation_requests + pel_requests
    all_requests.sort(key=lambda r: r.start_date)

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total = len(all_requests)
    total_pages = max(ceil(total / per_page), 1)  # Avoid division by zero

    # Clamp the page number
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    paginated_requests = all_requests[start:end]

    return render_template(
        "profile_page.html",
        user=user,
        all_requests=all_requests,
        paginated_requests=paginated_requests,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

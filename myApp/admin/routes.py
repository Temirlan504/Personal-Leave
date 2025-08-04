from datetime import datetime
import secrets
from myApp import bcrypt
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf
from myApp import db
from myApp.admin.forms import AddUserForm
from myApp.models import User
from myApp.admin.utils import generate_unique_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

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
        return redirect(url_for('admin.add_user'))

    users = User.query.all()
    return render_template('admin_add_user.html', form=form, users=users)

@admin_bp.route('/all-users')
@login_required
def all_users():
    if current_user.role not in ['hr', 'admin']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.date_joined.desc()).paginate(page=page, per_page=10)

    return render_template('admin_all_users.html', users=users)

@admin_bp.route('/user_detail/<int:user_id>')
@login_required
def user_detail(user_id):
    if current_user.role not in ['hr', 'admin']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    csrf_token = generate_csrf()
    return render_template('user_detail.html', user=user, csrf_token=csrf_token)

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role not in ['admin', 'hr']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself or the main admin
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')

    return redirect(url_for('admin.all_users'))

@admin_bp.route('/edit-user/<int:user_id>', methods=['POST'])
@login_required
def edit_user_inline(user_id):
    if current_user.role not in ['admin', 'hr']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)

    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.email = request.form.get('email')
    user.phone = request.form.get('phone')
    user.role = request.form.get('role')
    salary_str = request.form.get('base_salary')
    try:
        salary = float(salary_str)
        if salary <= 0:
            flash("Base salary must be greater than 0.", "danger")
            return redirect(url_for('admin.user_detail', user_id=user.id))
        user.base_salary = salary
    except (ValueError, TypeError):
        flash("Invalid base salary.", "danger")
        return redirect(url_for('admin.user_detail', user_id=user.id))
    date_str = request.form.get('date_joined')
    if date_str:
        try:
            user.date_joined = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format for Date Joined.", "danger")

    db.session.commit()
    flash("User updated successfully.", "success")
    return redirect(url_for('admin.user_detail', user_id=user.id))

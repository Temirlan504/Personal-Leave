import secrets
import bcrypt
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
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
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from myApp import db
from myApp.requests.forms import RequestForm
from myApp.models import Vacation, PEL
from myApp.requests.utils import process_vacation_request, process_pel_request
from functools import wraps
from myApp.users.utils import calculate_paid_pel_days, can_take_pel

requests_bp = Blueprint('requests', __name__)


@requests_bp.route('/pel_request', methods=['GET', 'POST'])
@login_required
def pel_request():
    form = RequestForm()
    pending_pel = PEL.query.filter_by(user_id=current_user.id).filter(PEL.status == 'pending').first()
    if pending_pel:
        flash("You already have a pending PEL request. Please wait for it to be processed.", "warning")
        return redirect(url_for('users.profile', user_id=current_user.id))
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        is_paid = form.is_paid.data == 'yes' if form.is_paid.data else False
        requested_days = (end_date - start_date).days + 1

        # Check for reverse or negative dates
        if start_date > end_date:
            flash("Invalid date range.", "danger")
            return redirect(url_for('requests.pel_request'))

        # Check limits using method in User model
        allowed, message = can_take_pel(current_user, requested_days)
        if not allowed:
            flash(message, 'danger')
            return redirect(url_for('requests.pel_request'))
        
        if is_paid:
            paid_days, unpaid_days = calculate_paid_pel_days(current_user, requested_days)
            if paid_days > 0 and unpaid_days > 0:
                flash(f"✅ PEL request submitted. You will be paid for {paid_days} day(s); the remaining {unpaid_days} will be unpaid.", "info")
            elif paid_days > 0:
                flash(f"✅ PEL request submitted. You will be paid for {paid_days} day(s).", "info")
            else:
                flash(f"✅ PEL request submitted. All {requested_days} day(s) will be unpaid.", "info")
        else:
            flash(f"✅ PEL request submitted. All {requested_days} day(s) will be unpaid.", "info")

        
        pel = PEL(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid=(form.is_paid.data == 'yes' if form.is_paid.data else False)
        )
        db.session.add(pel)
        db.session.commit()
        flash('PEL request submitted.')
        return redirect(url_for('users.profile', user_id=current_user.id))
    return render_template('pel_form.html', form=form, date=date)

@requests_bp.route('/vacation_request', methods=['GET', 'POST'])
@login_required
def vacation_request():
    form = RequestForm()
    # Check for existing pending Vacation request
    pending_vacation = Vacation.query.filter_by(user_id=current_user.id).filter(Vacation.status == 'pending').first()
    if pending_vacation:
        flash("You already have a pending vacation request. Please wait for it to be processed.", "warning")
        return redirect(url_for('users.profile', user_id=current_user.id))

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        is_paid = form.is_paid.data == 'yes' if form.is_paid.data else False
        requested_days = (end_date - start_date).days + 1

        # Check for reverse or negative dates
        if start_date > end_date:
            flash("Invalid date range.", "danger")
            return redirect(url_for('requests.vacation_request'))
        
        # Check if requested days exceed available vacation days
        if requested_days > current_user.vacation_days_total - current_user.vacation_days_taken:
            flash(f"You do not have enough vacation days available.", "danger")
            return redirect(url_for('requests.vacation_request'))

        vacation = Vacation(
            user_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_paid= is_paid
        )
        db.session.add(vacation)
        db.session.commit()
        flash('Vacation request submitted.', 'success')
        return redirect(url_for('users.profile', user_id=current_user.id))
    return render_template('vacation_form.html', form=form, date=date)


# Decorator to check if user is admin or HR
def admin_or_hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['admin', 'hr']:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@requests_bp.route('/request_detail/<string:request_type>/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_or_hr_required
def request_detail(request_type, request_id):
    request_obj = PEL.query.get(request_id) if request_type == 'pel' else Vacation.query.get(request_id)

    if not request_obj:
        flash("Request not found.", "danger")
        return redirect(url_for('main.home'))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "approve_admin" and current_user.role == "admin":
            request_obj.admin_approved = True
        elif action == "approve_hr" and current_user.role == "hr":
            request_obj.hr_approved = True
        elif action == "decline":
            request_obj.status = "declined"

        # Final approval logic
        if request_obj.admin_approved and request_obj.hr_approved:
            if request_type == 'pel':
                process_pel_request(request_obj, db)
            elif request_type == 'vacation':
                process_vacation_request(request_obj, db)

        db.session.commit()
        return redirect(url_for('requests.request_detail', request_type=request_type, request_id=request_id))

    return render_template('request_detail.html', req=request_obj)

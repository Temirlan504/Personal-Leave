from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from myApp import db

from myApp.requests.forms import RequestForm
from myApp.models import Vacation, PEL
from myApp.requests.utils import convert_dollars_to_days_hours

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
        is_paid = form.is_paid.data
        requested_days = (end_date - start_date).days + 1

        # Check limits using method in User model
        allowed, message = current_user.can_take_pel(is_paid, requested_days)
        if not allowed:
            flash(message, 'danger')
            return redirect(url_for('requests.pel_request'))
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
        is_paid = form.is_paid.data
        requested_days = (end_date - start_date).days + 1
        available_days = current_user.get_available_vacation_days()

        # Check for reverse or negative dates
        if start_date > end_date:
            flash("Start date cannot be after end date.", "danger")
            return redirect(url_for('requests.vacation_request'))

        if is_paid and requested_days > available_days:
            flash(f"You only have {available_days} paid vacation days left.", "danger")
            return redirect(url_for('requests.vacation_request'))

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
        return redirect(url_for('users.profile', user_id=current_user.id))
    return render_template('vacation_form.html', form=form, date=date)

@requests_bp.route('/request_detail/<string:request_type>/<int:request_id>', methods=['GET', 'POST'])
@login_required
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

        # Final approval
        if request_obj.admin_approved and request_obj.hr_approved:
            request_obj.status = "approved"

        db.session.commit()
        return redirect(url_for('requests.request_detail', request_type=request_type, request_id=request_id))

    return render_template('request_detail.html', req=request_obj)
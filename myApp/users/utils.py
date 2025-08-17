from flask import url_for
from myApp.email_service import send_password_reset_email

def send_reset_email(user):
    token = user.get_reset_token()
    send_password_reset_email(user.email, token)

def get_days_requested(start_date, end_date):
    return (end_date - start_date).days + 1

def can_take_pel(user, requested_days):
    if requested_days > user.pel_days_total - user.pel_days_taken:
        return False, "You do not have enough PEL days available."
    return True, None

def calculate_paid_pel_days(user, requested_days):
    approved_paid_days = sum(
        get_days_requested(p.start_date, p.end_date)
        for p in user.pel_requests
        if p.is_paid and p.status == 'approved'
    )
    paid_pel_remaining = max(3 - approved_paid_days, 0)
    paid_days = min(requested_days, paid_pel_remaining)
    unpaid_days = requested_days - paid_days
    return paid_days, unpaid_days

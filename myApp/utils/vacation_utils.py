from datetime import datetime

def calculate_vacation_accrual(user, current_date=None):
    current_date = current_date or datetime.utcnow()
    years_of_service = (current_date - user.date_joined).days // 365
    rate = 0.06 if years_of_service >= 5 else 0.04
    return rate
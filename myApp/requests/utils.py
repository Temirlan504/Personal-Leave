from myApp.users.utils import get_days_requested

def process_vacation_request(vacation, db):
    user = vacation.user
    days_requested = get_days_requested(vacation.start_date, vacation.end_date)

    user.vacation_days_taken += days_requested
    vacation.status = 'approved'
    db.session.commit()

def process_pel_request(pel, db):
    user = pel.user
    days_requested = get_days_requested(pel.start_date, pel.end_date)
    user.pel_days_taken += days_requested

    if pel.is_paid:
        paid_pel_remaining = 3 - sum(
            get_days_requested(p.start_date, p.end_date)
            for p in user.pel_requests
            if p.is_paid and p.status == 'approved'
        )
        paid_days = min(days_requested, paid_pel_remaining)

    pel.status = 'approved'
    db.session.commit()

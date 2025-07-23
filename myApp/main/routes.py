from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from myApp.models import Vacation, PEL
from myApp.main.utils import get_greeting

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
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
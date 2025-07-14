from datetime import datetime, date
from myApp import db, login_manager, app
from flask_login import UserMixin
from myApp.utils.image_utils import get_random_image
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default=get_random_image)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Employee')
    date_joined = db.Column(db.Date, nullable=False, default=date.today)
    base_salary = db.Column(db.Float, nullable=False, default=1.0)

    vacation_days = db.Column(db.Integer, default=14)
    paid_vacation_days = db.Column(db.Integer, default=0)
    paid_vacation_days_taken = db.Column(db.Integer, default=0)
    pel_days = db.Column(db.Integer, default=10)
    pel_requests = db.relationship('PEL', backref='user', lazy=True)
    vacation_requests = db.relationship('Vacation', backref='user', lazy=True)

    def get_paid_vacation_days_used(self):
        return sum(
            (v.end_date - v.start_date).days + 1
            for v in self.vacation_requests
            if v.is_paid and v.status == 'approved'
        )

    def get_available_vacation_days(self):
        return max(0, self.vacation_days - self.get_paid_vacation_days_used())

    def get_pay_periods_worked(self):
        return max(1, (date.today() - self.date_joined).days // 14)
    
    def get_total_vacation_accrued_dollars(self):
        return self.vacation_accrued_per_period() * self.get_pay_periods_worked()

    def vacation_accrued_per_period(self):
        return (0.04 if self.get_years_of_service() < 5 else 0.06) * self.base_salary / 26
    
    def get_years_of_service(self):
        return (date.today() - self.date_joined).days // 365

    @property
    def paid_pel_days_taken(self):
        return sum(
            (req.end_date - req.start_date).days + 1
            for req in self.pel_requests
            if req.is_paid and req.status == 'approved'
        )

    @property
    def pel_days_taken(self):
        return sum(
            (req.end_date - req.start_date).days + 1
            for req in self.pel_requests
            if req.status == 'approved'
        )

    def can_take_pel(self, is_paid, requested_days):
        total_pel_taken = sum(
            (req.end_date - req.start_date).days + 1
            for req in self.pel_requests
            if req.status in ['approved', 'pending']
        )
        if total_pel_taken + requested_days > 10:
            return False, "Exceeded 10 total PEL days."

        paid_remaining = max(0, 3 - self.paid_pel_days_taken)
        if is_paid and requested_days > paid_remaining:
            msg = f"Successfully submitted PEL request.\
                ⚠ Only {paid_remaining} PEL days will be paid. Remaining will be unpaid."
            return True, msg  # allow with info
        
        return True, ""

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'], expires_in=1800)
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.email}', '{self.role}')"


class PEL(db.Model):
    __tablename__ = 'pel'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'declined'
    type = db.Column(db.String(20), default='PEL')  # used for displaying leave type

    def __repr__(self):
        return f"PEL('{self.user.email}', '{self.start_date}', '{self.end_date}', '{self.is_paid}')"


class Vacation(db.Model):
    __tablename__ = 'vacation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    type = db.Column(db.String(20), default='Vacation')

    def __repr__(self):
        return f"Vacation('{self.user.email}', '{self.start_date}', '{self.end_date}', '{self.is_paid}')"

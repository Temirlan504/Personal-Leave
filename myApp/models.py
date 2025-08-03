from datetime import datetime, date
from myApp import db, login_manager
from flask_login import UserMixin
import random
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app as app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_random_image():
    return f"profile_pics/monster{random.randint(1, 10)}.png"

class User(db.Model, UserMixin):
    __tablename__ = 'user'
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

    vacation_days_total = db.Column(db.Integer, default=14, nullable=False)
    vacation_days_taken = db.Column(db.Integer, default=0, nullable=False)
    vacation_requests = db.relationship('Vacation', backref='user', lazy=True)

    pel_days_total = db.Column(db.Integer, default=10, nullable=False)
    pel_days_paid = db.Column(db.Integer, default=3, nullable=False) # Employees entitled to 3 paid PEL days out of 10 total
    pel_days_taken = db.Column(db.Integer, default=0, nullable=False)
    pel_requests = db.relationship('PEL', backref='user', lazy=True)

    # Methods for password management
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
    admin_approved = db.Column(db.Boolean, default=False)
    hr_approved = db.Column(db.Boolean, default=False)

    @property
    def is_fully_approved(self):
        return self.admin_approved and self.hr_approved

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
    admin_approved = db.Column(db.Boolean, default=False)
    hr_approved = db.Column(db.Boolean, default=False)

    @property
    def is_fully_approved(self):
        return self.admin_approved and self.hr_approved

    def __repr__(self):
        return f"Vacation('{self.user.email}', '{self.start_date}', '{self.end_date}', '{self.is_paid}')"

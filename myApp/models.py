from myApp import db, login_manager
from flask_login import UserMixin
from myApp.utils.image_utils import get_random_image

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
    role = db.Column(db.String(20), nullable=False, default='employee')  # Default role is 'employee'

    vacation_days = db.Column(db.Integer, default=14)  # Default vacation days
    pel_days = db.Column(db.Integer, default=5)  # Default personal emergency leave days (sick days)
    paid_vacation_days = db.Column(db.Integer, default=0)  # Paid vacation days taken
    paid_pel_days = db.Column(db.Integer, default=0)  # Paid personal emergency leave days taken

    def __repr__(self):
        return f"User('{self.email}', '{self.role}')"

import random
from flask import request, url_for
from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '4v36non75hbv8oqu3f7c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Models
def get_random_image():
    return f"profile_pics/monster{random.randint(1, 3)}.png"
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default=get_random_image)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.phone}', '{self.image_file}')"


# Define the homepage routes
@app.route('/')
def home():
    users = User.query.all()  # Fetch all users from the database
    greeting = get_greeting()  # e.g. "morning", "afternoon", etc.
    return render_template("homepage.html",
        greeting=greeting,
        vacation_days_left=10,
        vacation_days_total=14,
        pel_days_left=2,
        pel_days_total=5,
        users=users
    )

def get_greeting():
    try:
        current_hour = datetime.now().hour
        if 0 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 18:
            return "Good afternoon"
        elif 18 <= current_hour <= 23:
            return "Good evening"
        else:
            return "Hello"  # Fallback for unexpected hour values
    except Exception:
        return "Hello"  # Fallback for any error (e.g. datetime failure)
    

# Define the login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'alice@example.com' and form.password.data == 'password':
            return redirect('/')
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template("login.html", form=form)


# Define profile page routes
@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile_page.html", user=user)

# Application entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, flash, redirect
from datetime import datetime
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '4v36non75hbv8oqu3f7c'

users = [
    {'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@example.com', 'phone': '123-456-7890'},
    {'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob@example.com', 'phone': '987-654-3210'}
]

@app.route('/')
def home():
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
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'alice@example.com' and form.password.data == 'password':
            return redirect('/')
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template("login.html", form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

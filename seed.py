from datetime import date
from myApp import bcrypt, db, create_app
from myApp.models import User

app = create_app()

with app.app_context():
    # --- Admin ---
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            phone='123-456-7890',
            image_file='default.jpg',
            password=bcrypt.generate_password_hash('admin').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)

    # --- HR ---
    if not User.query.filter_by(email='humanr@example.com').first():
        hr = User(
            first_name='Human',
            last_name='Resources',
            email='humanr@example.com',
            image_file='default.jpg',
            password=bcrypt.generate_password_hash('humanr').decode('utf-8'),
            role='hr'
        )
        db.session.add(hr)

    # --- Employee ---
    if not User.query.filter_by(email='temirlany@example.com').first():
        employee = User(
            first_name='Temirlan',
            last_name='Yergazy',
            email='temirlany@example.com',
            phone='905-925-9500',
            image_file='default.jpg',
            password=bcrypt.generate_password_hash('employee').decode('utf-8'),
            role='employee',
            base_salary=21.63,  # Hourly rate
            date_joined=date(2025, 9, 2),
        )
        db.session.add(employee)

    db.session.commit()
    print("✅ Users seeded successfully")

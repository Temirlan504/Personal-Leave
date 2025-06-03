from myApp.models import User

def generate_unique_email(first_name, last_name, domain="example.com"):
    base = f"{first_name.lower()}{last_name[0].lower()}"
    email = f"{base}@{domain}"
    count = 1

    while User.query.filter_by(email=email).first():
        email = f"{base}{count}@{domain}"
        count += 1

    return email
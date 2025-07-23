from flask_wtf import FlaskForm
from wtforms import (
    PasswordField, SubmitField, BooleanField, EmailField,
    ValidationError
)
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=25)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Contact support.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=25)])
    submit = SubmitField('Reset Password')

    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.password.data:
            raise ValidationError('Passwords must match.')
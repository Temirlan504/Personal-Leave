from flask_wtf import FlaskForm
from wtforms import (
    DateField, PasswordField, SelectField, StringField,
    SubmitField, BooleanField, EmailField,
    RadioField, FloatField, ValidationError
)
from wtforms.validators import DataRequired, Email, Length
from myApp.models import User
from datetime import date

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=25)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=40)])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('employee', 'Employee'), ('hr', 'HR')], default='employee')
    date_joined = DateField('Date Joined (YYYY-MM-DD)', validators=[DataRequired()])
    base_salary = FloatField('Base Salary', validators=[DataRequired()])
    submit = SubmitField('Add User')
    
class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=40)])
    phone = StringField('Phone Number', validators=[Length(max=15)])
    password = PasswordField('Password', validators=[Length(min=6, max=25)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('employee', 'Employee'), ('hr', 'HR')], default='employee')
    date_joined = DateField('Date Joined (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

class RequestForm(FlaskForm):
    start_date = DateField('Start Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    is_paid = RadioField('Request pay?', choices=[('yes', 'Yes'), ('no', 'No')], validators=[DataRequired()])
    submit = SubmitField('Submit PEL Request')

    def validate_start_date(self, start_date):
        if start_date.data < date.today():
            raise ValidationError('Start date must be today or in the future.')

    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError('End date must be after start date.')

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
from flask_wtf import FlaskForm
from wtforms import (
    DateField, PasswordField, SelectField, StringField,
    SubmitField, FloatField
)
from wtforms.validators import DataRequired, Length

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
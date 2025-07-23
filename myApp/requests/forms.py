from flask_wtf import FlaskForm
from wtforms import DateField, RadioField, SubmitField, ValidationError
from datetime import date
from wtforms.validators import DataRequired


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
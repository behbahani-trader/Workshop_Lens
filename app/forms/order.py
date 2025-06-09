from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime

class OrderForm(FlaskForm):
    customer_id = SelectField('مشتری', coerce=int, validators=[DataRequired()])
    created_at = DateField('تاریخ ثبت', validators=[DataRequired()], default=datetime.utcnow)
    payment = FloatField('پرداختی', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('یادداشت‌ها') 
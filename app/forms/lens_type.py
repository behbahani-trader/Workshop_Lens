from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange

class LensTypeForm(FlaskForm):
    name = StringField('نام', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('توضیحات')
    default_price = FloatField('قیمت پیش‌فرض', validators=[DataRequired(), NumberRange(min=0)]) 
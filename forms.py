from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class SearchResaleHDBForm(FlaskForm):
    streetname = StringField('Street Name', validators=[DataRequired(), Length(min=2, max=20)])
    dropdown_list = ['1', '2', '3', '4', '5']
    bedrooms = SelectField('Bedrooms', choices=dropdown_list, default=1)
    submit = SubmitField('Search')
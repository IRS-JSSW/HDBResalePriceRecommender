from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
import datetime

class SearchResaleHDBForm(FlaskForm):
    streetname = StringField('Street Name', validators=[DataRequired(), Length(min=2, max=20)])
    dropdown_list_bedrooms = ['1', '2', '3', '4', '5']
    bedrooms = SelectField('Bedrooms', choices=dropdown_list_bedrooms, default=1)
    dropdown_list_completion = list(range(1960, datetime.datetime.today().year))
    completion = SelectField('Year of completion', choices=dropdown_list_completion, default=dropdown_list_completion[-1])
    submit = SubmitField('Search')

class UpdateResaleHDBForm(FlaskForm):
    confirm_update = SelectField('Update Data?', choices=['Yes', 'No'], default=1)
    update = SubmitField('Update')
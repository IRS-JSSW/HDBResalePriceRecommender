from flask_wtf import FlaskForm
from wtforms import Form, StringField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL
import datetime

class CustomValidators(Form):
    def __call__(self,form,field):
        if (field.data).startswith("https://www.propertyguru.com.sg/") != True:
            raise ValidationError("Please use a valid PropertyGuru URL.")

class SearchResaleHDBForm(FlaskForm):
    streetname = StringField('Propertyguru URL', validators=[DataRequired(), URL(require_tld=True), CustomValidators()])
    # dropdown_list_bedrooms = ['1', '2', '3', '4', '5']
    # bedrooms = SelectField('Bedrooms', choices=dropdown_list_bedrooms, default=1)
    # dropdown_list_completion = list(range(1960, datetime.datetime.today().year))
    # completion = SelectField('Year of completion', choices=dropdown_list_completion, default=dropdown_list_completion[-1])
    submit = SubmitField('Search')

class UpdateDataGovForm(FlaskForm):
    confirm_update1 = SelectField('Update Data Gov Table?', choices=['Yes', 'No'], default=1)
    update1 = SubmitField('Update')

class UpdatePropGuruForm(FlaskForm):
    confirm_update2 = SelectField('Update Propertyguru Table?', choices=['Yes', 'No'], default=1)
    update2 = SubmitField('Update')
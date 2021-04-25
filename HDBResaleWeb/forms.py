from flask_wtf import FlaskForm
from wtforms import Form, StringField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL
import datetime

class CustomValidators(Form):
    def __call__(self,form,field):
        if (field.data).startswith("https://www.propertyguru.com.sg/listing/hdb-for-sale") != True:
            raise ValidationError("Please use a valid PropertyGuru HDB listing URL.")

class SearchResaleHDBForm(FlaskForm):
    streetname = StringField('Propertyguru URL (Paste Propertyguru URL in the box below)', validators=[DataRequired(), URL(require_tld=True), CustomValidators()])
    submit = SubmitField('Search')

class UpdateDataGovForm(FlaskForm):
    confirm_update1 = SelectField('Update Data Gov Table?', choices=['Yes', 'No'], default=1)
    update1 = SubmitField('Update')

class UpdatePropGuruForm(FlaskForm):
    confirm_update2 = SelectField('Update Propertyguru Table?', choices=['Yes', 'No'], default=1)
    update2 = SubmitField('Update')

class UpdateModelForm(FlaskForm):
    confirm_update3 = SelectField('Update Training Model?', choices=['Yes', 'No'], default=1)
    update3 = SubmitField('Train')

class UpdateAmenitiesForm(FlaskForm):
    confirm_update4 = SelectField('Update Amenities Table?', choices=['Yes', 'No'], default=1)
    update4 = SubmitField('Update')
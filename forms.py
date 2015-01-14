from flask_wtf import Form
from wtforms import StringField, RadioField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(Form):

    zipcode = StringField(label='Zip Code')
    country = StringField(label='Country')
    state = StringField(label='State')
    city = StringField(label='City')
    user_name = StringField(label='User Name')
    submit_user = SubmitField('Search by YOUR ACCOUNT')
    submit_place = SubmitField('Search by PLACE')
    submit_zip = SubmitField('Search by ZIP CODE')


class SchoolForm(Form):
    #need error message if required data is not submitted.
    user_name = StringField(label='User Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    school_name = StringField(label='School', validators=[DataRequired()])
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    city = StringField(label='City', validators=[DataRequired()])
    state = StringField(label='State', validators=[DataRequired()])
    postal = StringField(label='Postal Code', validators=[DataRequired()])
    country = StringField(label='Country', validators=[DataRequired()])
    cellphone = StringField(label='Cell Phone', validators=[DataRequired()])
    send_email = BooleanField(label='Send me email every morning', default=True)
    send_text = BooleanField(label='Send me text every morning', default=True)

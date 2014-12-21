from flask_wtf import Form
from wtforms import StringField, RadioField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(Form):
    search_by = RadioField( choices=[('postal', 'Postal'),('place','Place'), ('code', 'Code')],
                            validators=[DataRequired(),])
    postal = StringField(label='Postal Code')
    country = StringField(label='Country', default="US")
    state = StringField(label='State')
    city = StringField(label='City')
    code = StringField(label='CECE Code')


class SchoolForm(Form):
    CECE_code = StringField(label='CECE code')
    email = StringField(label='Email', validators=[DataRequired()])
    school_name = StringField(label='School', validators=[DataRequired()])
    first_name = StringField(label='First Name', validators=[DataRequired()])
    last_name = StringField(label='Last Name', validators=[DataRequired()])
    city = StringField(label='City', validators=[DataRequired()])
    state = StringField(label='State', validators=[DataRequired()])
    postal = StringField(label='Postal Code', validators=[DataRequired()])
    country = StringField(label='Country', validators=[DataRequired()])
    cellphone = StringField(label='Country', validators=[DataRequired()])
    send_email = BooleanField(label='Send me email every morning', default=True)
    send_text = BooleanField(label='Send me text every morning', default=True)

from flask_wtf import Form
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired

class SearchForm(Form):
    search_by = RadioField( choices=[('postal', 'Postal'),('place','Place'), ('code', 'Code')],
                            validators=[DataRequired(),])
    postal = StringField(label='Postal Code')
    country = StringField(label='Country', default="US")
    state = StringField(label='State')
    city = StringField(label='City')
    code = StringField(label='CECE Code')



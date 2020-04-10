from wtforms import Form, StringField, TextAreaField, PasswordField, validators,DateTimeField,IntegerField, SelectField
from wtforms.validators import Length, InputRequired

class DetailForm(Form):

    regions = [
        ('', ('Choose')),
        ('supermarket', ('Grocery / Supermarket')),
        ('pharmacy', ('Pharmacy'))     
        ]
    user_address  = StringField('Location', validators=[InputRequired(), Length(min=1, max=100)])
    store_type = SelectField('Type of Store',choices=regions,validators= [InputRequired(), Length(min=1,max=100)])
    radius = StringField('Upto travel (In mtrs)', validators=[InputRequired(), Length(min=1, max=5)])
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

class UserForm(Form):

    fname = StringField('First Name', validators=[InputRequired(), Length(min=1, max=100)])
    lname = StringField('Last Name', validators=[InputRequired(), Length(min=1, max=100)])
    email = StringField('Email ID', validators=[InputRequired(), Length(min=1, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=10, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=10, max=100)])

class UserLogin(Form):

    email = StringField('Email ID', validators=[InputRequired(), Length(min=1, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=10, max=100)])

class NGOForm(Form):

    name = StringField('First Name', validators=[InputRequired(), Length(min=1, max=100)])
    email = StringField('Email ID', validators=[InputRequired(), Length(min=1, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=10, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=10, max=100)])
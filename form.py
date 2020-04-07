from wtforms import Form, StringField, TextAreaField, PasswordField, validators,DateTimeField,IntegerField

class DetailForm(Form):
    user_address  = StringField('Location', [validators.Length(min=1, max=100)])
    store_type = StringField('Type of Store',[validators.Length(min=1,max=100)])
    radius = StringField('Upto travel (In mtrs)', [validators.Length(min=1, max=100)])
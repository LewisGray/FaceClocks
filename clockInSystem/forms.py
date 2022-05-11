from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField,SelectField,IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length,Email,EqualTo
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    firstName = StringField('First Name',validators=[DataRequired(),Length(min=2,max=15)])
    lastName = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=15)])
    isAdmin = BooleanField('Admin?')
    image = FileField('Photo for recognition', validators=[FileAllowed(['jpg'])])
    submit = SubmitField('Register Attendee')


class AttendeeForm(FlaskForm):
    attendee = SelectField('Select an attendee')

class InfoForm(FlaskForm):
    date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')
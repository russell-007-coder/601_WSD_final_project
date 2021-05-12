from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp, EqualTo
from wtforms_components import EmailField, Email
from wtforms_alchemy.validators import Unique
from wtforms.validators import ValidationError
from manager.models.Users import Users
from manager.ext import db

class ModelForm(FlaskForm):
    def __init__(self, obj=None, prefix='', **kwargs):
        FlaskForm.__init__(
            self, obj=obj, prefix=prefix, **kwargs
        )
        self._obj = obj

def ensure_identity_exists(form, field):
    user = Users.find_by_identity(field.data)

    if not user:
        raise ValidationError('Unable to locate account.')


def ensure_existing_password_matches(form, field):
    user = Users.query.get(form._obj.id)

    if not user.authenticated(password=field.data):
        raise ValidationError('Does not match.')


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username or email', validators=[DataRequired(), Length(3, 254)])
    password = PasswordField('Password',  validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Stay signed in')    


class BeginPasswordResetForm(FlaskForm):
    identity = StringField('Username or email', validators=[DataRequired(), Length(3, 254), ensure_identity_exists])


class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField('Password',  validators=[DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    username = StringField(validators=[DataRequired(), Unique(Users.username, get_session=lambda: db.session)])
    email = EmailField(validators=[DataRequired(), Email(), Unique(Users.email, get_session=lambda: db.session)])
    password = PasswordField(validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')])


class SendEmailAgainForm(ModelForm):
    send = SubmitField('Send Again')


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Current password', 
                            [DataRequired(), Length(8, 128), ensure_existing_password_matches])
    email = EmailField( validators=[ Email(), Unique( Users.email, get_session=lambda: db.session)])
    password = PasswordField('Password', [Optional(), Length(8, 128)])


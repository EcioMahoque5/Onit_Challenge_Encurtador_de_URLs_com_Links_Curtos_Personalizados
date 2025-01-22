from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, Optional
import re


def validate_domain(domain):
    # Regex for validating a domain
    domain_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}$"
    return re.match(domain_regex, domain) is not None

class UserRegistrationForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message="username is a required field!"), 
        Length(min=4, max=16,message="username must have 4-16 characters!")])
    
    password = PasswordField('password', validators=[
        DataRequired(message="password is a required field!"),
        Regexp(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*()_+-=]).{8,32}$',
                message='password must include at least one uppercase letter, one lowercase letter, one number, and one special character, and be between 8 and 32 characters long'
        )
    ])
    
    def __init__(self, *args, data_store=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_store = data_store or []
    
    def validate_username(self, field):
        if field.data in self.data_store:
            raise ValidationError('username already exists!')
        
        
class LoginForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message="username is a required field!")])
    
    password = PasswordField('password', validators=[
        DataRequired(message="password is a required field!")])
    
class ShortenLinkForm(FlaskForm):
    originalUrl = StringField('originalUrl', validators=[
        DataRequired(message="originalUrl is a required field!")])
    
    customShortLink = PasswordField('customShortLink', validators=[
        Optional(),
        DataRequired(message="customShortLink is a required field!")])
    
    domain = PasswordField('domain', validators=[
        Optional(),
        DataRequired(message="domain is a required field!")])
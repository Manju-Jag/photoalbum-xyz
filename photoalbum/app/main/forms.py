from re import UNICODE
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Email, EqualTo, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')    

class CreateAlbumForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Search for Album Category:', choices = [('flowers', 'Flowers'),
                                      ('animals', 'Animals'),
                                      ('sports', 'Sports'),
                                      ('nature', 'Nature'),
                                      ('other', 'Others')])
    is_favourite = BooleanField('Favourite')
    submit = SubmitField('Create')

class EditAlbumForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Search for Album Category:', choices = [('flowers', 'Flowers'),
                                      ('animals', 'Animals'),
                                      ('sports', 'Sports'),
                                      ('nature', 'Nature'),
                                      ('other', 'Others')])
    is_favourite = BooleanField('Favourite')
    update = SubmitField('Update')    


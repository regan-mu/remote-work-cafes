from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, EmailField,
                     SelectField, URLField, TimeField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Email, Length


# Add Cafe Form
class Cafes(FlaskForm):
    coffee_options = ['☕', '☕☕', '☕☕☕', '☕☕☕☕', '☕☕☕☕☕']
    wifi_options = ['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪', '💪💪💪💪💪']
    power_options = ['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌', '🔌🔌🔌🔌🔌']
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    map_link = URLField('Google Map Link', validators=[DataRequired()])
    image_url = URLField('Image Url', validators=[DataRequired()])
    coffee = SelectField('Coffee Rating', choices=coffee_options)
    wifi = SelectField('WiFi Strength', choices=wifi_options)
    power = SelectField('Available Power Sockets', choices=power_options)
    opening = TimeField('Opening Time', validators=[DataRequired()])
    closing = TimeField('Closing Time', validators=[DataRequired()])
    description = TextAreaField('Cafe Description', validators=[DataRequired(), Length(max=300)])
    submit = SubmitField('Add Cafe')

    # Check whether the cafe already exists in the database


# Comments Form
class Comments(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    text = TextAreaField('Comment', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Submit')


# Registration Form
class Register(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')


# Login Form
class Login(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Add Review Form
class Rating(FlaskForm):
    rating_vals = [1, 2, 3, 4, 5]
    rating = SelectField('Review', choices=rating_vals)
    submit = SubmitField('Submit Review')

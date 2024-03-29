# This library offers many more possibilities to create forms using classes
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, 
    StringField, 
    SubmitField, 
    TextAreaField, 
    URLField, 
    PasswordField
    )
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo

# FlaksForm protects us from CSRF attacks
class MovieForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()]) # Title is the label of the field
    director = StringField("Director", validators=[InputRequired()])
    
    year = IntegerField(
        "Year", 
        validators=[
            InputRequired(), 
            NumberRange(min=1878, message="Please enter a year in the format YYYY.")
        # Make sure to keep this order of validators !
        ]
    )
    submit = SubmitField("Add Movie")
    

# Class to adjust the TextAreaField class, to ensure we receive the textarea-input as a list of strings
class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
    
    # process_formdata() is an method which already exist in TextAreaField, but here we are modifying it
    # This 'method' will take in a string and splits it into a list of string for each new line
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []

# Now we create a form to edit a movieform which already exists
class ExtendedMovieForm(MovieForm):
    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description = TextAreaField("Description")
    video_link = URLField("Video link")

    submit = SubmitField("Submit") 

# Form to register
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(
                min=4, max=20, message="Your password must be between 4 and 20 characters long." 
            )
        ])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password did not match the one in the password field."
            ) ]
    )
    submit = SubmitField("Register")

# Form to login
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

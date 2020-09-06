from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_wtf.file import FileField, FileAllowed


# Form classes
###

# Registration form
class RegisterForm(Form):
    name = StringField('Name', [
        validators.Length(min=1, max=50),
        validators.DataRequired()
    ])
    username = StringField('Username', [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField('Email', [
        validators.Length(min=6, max=50),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password', [
        validators.DataRequired()
    ])


# Login Form
class LoginForm(Form):
    email = StringField('', [
        validators.DataRequired()
    ],
    render_kw={"placeholder": "Email or Username"})
    password = PasswordField('', [
        validators.DataRequired()
    ],
    render_kw={"placeholder": "Password"})



# Add article Form
class ArticleForm(Form):
    title = StringField('Article Title', [validators.Length(min=1, max=200)],
                        render_kw={"placeholder": "The Great Comedian"})
    body = TextAreaField('Article Content', [validators.Length(min=20)],
                         render_kw={"placeholder": "What do you think about the great comedian?"})
    image = FileField('Upload an image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
    ])

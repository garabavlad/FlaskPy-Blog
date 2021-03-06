from flasky import app
from authlib.integrations.flask_client import OAuth
import os
import stripe

# admin accounts
app.config['ADMIN_LIST'] = ['garaba1u', 'garaba.vlad@gmail.com'] # you might put in ur email or username for admin privileges

# setting app secret
app.secret_key = os.environ['SECRET_KEY'] # replace with your own secret string

# DATABASE MySQL config
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST'] # use the database credentials from repo or feel free to use ur own db
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuring Flask-Mail
app.config['MAIL_SERVER']  = 'smtp.gmail.com'  # set ur smtp server
app.config['MAIL_PORT']  = 465
app.config['MAIL_USE_SSL']  = True
app.config['MAIL_USERNAME']  = os.environ['SMTP_USERNAME'] # replace with smtp connexion username
app.config['MAIL_PASSWORD']  = os.environ['SMTP_PASSWORD'] # replace with your own smtp password
app.config['MAIL_DEFAULT_SENDER']  = 'no-reply@flasky-article-app.herokuapp.com'
app.config['MAIL_MAX_EMAILS']  = None
app.config['MAIL_ASCII_ATTACHMENTS']  = False

# Config for file uploading
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']
app.config['ALLOWED_EXTENSIONS'] = {'png','jpeg','jpg'}

# Stripe configuration
stripe.api_key = os.environ['STRIPE_SECRET_KEY']
app.config['STRIPE_PUBLISHABLE_KEY'] = os.environ['STRIPE_PUBLISHABLE_KEY']

# Google OAuth2 registration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ['GOOGLE_OAUTH2_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_OAUTH2_CLIENT_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)
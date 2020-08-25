from flasky import app
import os

# admin accounts
app.config['ADMIN_LIST'] = ['garaba1u', 'garaba.vlad@gmail.com']

# setting app secret
app.secret_key = os.environ['SECRET_KEY']

# DATABASE MySQL config
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuring Flask-Mail
app.config['MAIL_SERVER']  = 'smtp.gmail.com'
app.config['MAIL_PORT']  = 465
app.config['MAIL_USE_SSL']  = True
app.config['MAIL_USERNAME']  = os.environ['SMTP_USERNAME']
app.config['MAIL_PASSWORD']  = os.environ['SMTP_PASSWORD']
app.config['MAIL_DEFAULT_SENDER']  = 'no-reply@flasky-article-app.herokuapp.com'
app.config['MAIL_MAX_EMAILS']  = None
app.config['MAIL_ASCII_ATTACHMENTS']  = False
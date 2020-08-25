from flasky import app

# admin accounts
app.config['ADMIN_LIST'] = ['garaba1u', 'garaba.vlad@gmail.com']

# setting app secret
app.secret_key = 'dasWF@#56$VP"as1'

# DATABASE MySQL config
app.config['MYSQL_HOST'] = 'j1r4n2ztuwm0bhh5.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'apgcuzyplwnhtpzf'
app.config['MYSQL_PASSWORD'] = 'wibpgq8uv06eciat'
app.config['MYSQL_DB'] = 'fwtyv7la1cjn796i'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuring Flask-Mail
app.config['MAIL_SERVER']  = 'smtp.gmail.com'
app.config['MAIL_PORT']  = 465
app.config['MAIL_USE_SSL']  = True
app.config['MAIL_USERNAME']  = 'garaba.vlad1@gmail.com'
app.config['MAIL_PASSWORD']  = 'leopartino0'
app.config['MAIL_DEFAULT_SENDER']  = 'no-reply@flasky-article-app.herokuapp.com'
app.config['MAIL_MAX_EMAILS']  = None
app.config['MAIL_ASCII_ATTACHMENTS']  = False
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)

#importing app configurations
import flasky.config

# setting up the mailing service
mail = Mail(app)

#importing views
import flasky.views

#importing error handlers
import flasky.errors

#importing processors
import flasky.processors


# application initialization
if __name__ == '__main__':
    app.run(debug=True)

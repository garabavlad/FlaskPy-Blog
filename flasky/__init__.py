from flask import Flask

app = Flask(__name__)

# ADMIN ACCOUNTS
app.config['ADMIN_LIST'] = ['garaba1u', 'garaba.vlad@gmail.com']
# setting app secret
app.secret_key = 'dasWF@#56$VP"as1'

#importing views
import flasky.views

#importing error handlers
import flasky.errors

#importing processors
import flasky.processors


# application initialization
if __name__ == '__main__':
    app.run(debug=True)

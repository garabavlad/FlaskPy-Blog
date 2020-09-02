# Flasky Blog App

A CRUD Flask Py application for creating, displaying, and managing articles. 
Users can create and manege their content using the dashboard.

The application is using a MySQL database on JawsDB server

The application can be seen live on [this Demo](https://flasky-article-app.herokuapp.com/).

## Usage
First thing first - configuration. Check [config file](./flasky/config.py) and replace with your own credentials where indicated.


In order to use the application we need to export the module which will be used as starting point.

<summary>Open a terminal window in application folder and type:</summary>

```
export FLASK_APP=flasky
export FLASK_ENV=development
```

<summary>For Windows cmd:</summary>

```
set FLASK_APP=flasky
set FLASK_ENV=development
```

<summary>After you export the module, start the flask app:</summary>

```
pip install -e .
flask run
```

## Database
 The database credentials can be seen below, as I intend to leave them public for testing purposes.

 ``` json
 {
    "MYSQL_HOST" : "j1r4n2ztuwm0bhh5.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
    "MYSQL_USER" : "apgcuzyplwnhtpzf",
    "MYSQL_PASSWORD" : "wibpgq8uv06eciat",
    "MYSQL_DB" : "fwtyv7la1cjn796i"
}
```

## Features
 From all the features included in this app, I'd like to point out the most important ones:
 <details><summary>Click to see feature list</summary>
        <ul>
            <li>Bootstrap4, Fontawesome and GoogleFonts for creating website UI/UX.</li>
            <li>JawsDB for creating and managing database tables.</li>
            <li>App is currently hosted on Heroku.</li>
            <li>Using Git alongside app development.</li>
            <li>OAuth2 integration with Google.</li>
            <li>Google reCAPTCHA v3 on login and register pages.</li>
            <li>Using WTForms for validating Flask forms.</li>
            <li>Integrated Stripe and PayPal payment methods.</li>
            <li>Integrated Flask-mail for sending mails.</li>
            <li>Using Crypto for encrypting and generating user activation tokens.</li>
            <li>Allowed users to upload images for thier articles.</li>
            <li>Share buttons for Facebook and Twitter on article pages.</li>
            <li>Created user dashboard to manage their personal articles.</li>
            <li>Using CKEditor for creating a well formatted text for articles.</li>
            <li>Using flask processors to clear and select data to display on articles thumbnail.</li>
            <li>Using flask processors to generate a unique and random color for each article on Artciles page.</li>
            <li>Using @wraps to create middleware for user authentication.</li>
            <li>Flask error handling for HTTP 400,404 and 500 errors.</li>
        </ul>
   </details>

Have fun!


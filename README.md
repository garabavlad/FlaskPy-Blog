# Flasky Blog App

A CRUD Flask Py application for creating, displaying, and managing articles. 
Users can create and manege their content using the dashboard.

The application is using a MySQL database on JawsDB server

The application can be seen live on [this Demo](https://flasky-article-app.herokuapp.com/).

## Usage
First this first - check [Config file](./flasky/config.py) and replace with your own details.


In order to use the application we need to export the module which will be used as starting point.
Open a terminal window in application folder and type:

```
export FLASK_APP=flasky
export FLASK_ENV=development
```

For Windows cmd:
```
set FLASK_APP=flasky
set FLASK_ENV=development
```

After you export the module, run the following commands to start the server:
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

Have fun!

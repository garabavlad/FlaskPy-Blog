# Flasky Blog App

A CRUD Flask Py application for creating, displaying, and managing articles. 
Users can create and manege their content using the dashboard.

The application is using a MySQL database on JawsDB server

The application can be seen live on [this Demo](https://flasky-article-app.herokuapp.com/).

## Usage

Open a terminal window in application folder and include

```export FLASK_APP=flasky```
```export FLASK_ENV=development```

```pip install -e .
flask run```


## Database
 The database credentials can be seen [here](./flasky/views.py) and I intend to leave it public.

 ``` json
 {
    'MYSQL_HOST' : 'j1r4n2ztuwm0bhh5.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
    'MYSQL_USER' = 'apgcuzyplwnhtpzf',
    'MYSQL_PASSWORD' = 'wibpgq8uv06eciat',
    'MYSQL_DB' = 'fwtyv7la1cjn796i'
}
```

Enjoy!

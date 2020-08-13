from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from WTFormClasses import RegisterForm, LoginForm, ArticleForm

app = Flask(__name__)

# DATABASE
# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'leopartino0'
app.config['MYSQL_DB'] = 'flasky'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)


# Wraps
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized access to the page.', 'danger')
            return redirect(url_for('login'))

    return wrap


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# About page
@app.route('/about')
def about():
    return render_template('about.html')


# All Articles page
@app.route('/articles')
def articles():
    # connect to db & get articles
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()
    cur.close()

    return render_template('articles.html', articles=articles)


# Article page
@app.route('/articles/<string:id>/')
def article(id):
    # connect to db & get article info
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    return render_template('article.html', article = article)


# Support page
@app.route('/support')
def support():
    return render_template('support.html')


# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        # getting form values
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # creating cursor
        cur = mysql.connection.cursor()

        # submit to DB
        cur.execute("INSERT INTO users (name,email,username,password) VALUES (%s, %s, %s, %s)",
                    (name, email, username, password))

        # commit changes & close connection
        mysql.connection.commit()
        cur.close()

        flash("You are now registered and can log in!", "success")
        return redirect(url_for("login"))

    elif request.method == 'GET':
        pass

    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = request.form['email']
        password_candidate = request.form['password']

        # creating cursor
        cur = mysql.connection.cursor()

        # submit to DB & close connection
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # compare passwrds
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = email

                flash("You are now logged in!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("The email or password didn't match!", "danger")
        else:
            flash("The email or password didn't match", "danger")

        cur.close()
    return render_template('login.html', form=form)


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # connect to db & get articles
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', articles = articles)


# Add article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)

    if(request.method=='POST' and form.validate()):
        title = form.title.data
        body = form.body.data

        # database logic
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title,body,author) VALUES (%s,%s,%s)", (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('New article successfully created!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

@app.route('/delete_article/<string:id>/')
@is_logged_in
def delete_article(id):

    # database logic
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id=%s and author = %s", (id, session['username']))
    mysql.connection.commit()
    cur.close()

    flash('The article with id %s was successfully deleted!' % (id), 'success')
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('index'))


# running the application
if __name__ == '__main__':
    app.secret_key = 'DA!@BB^&%434SD@#pz'
    app.run(debug=True)

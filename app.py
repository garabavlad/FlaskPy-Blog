from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, make_response, Markup
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from WTFormClasses import RegisterForm, LoginForm, ArticleForm

app = Flask(__name__)

# ADMIN ACCOUNTS
app.config['ADMIN_LIST'] = ['garaba1u', 'garaba.vlad@gmail.com']

# setting app secret
app.secret_key = 'dasWF@#56$VP"as1'

# DATABASE
# MySQL config
app.config['MYSQL_HOST'] = 'j1r4n2ztuwm0bhh5.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'apgcuzyplwnhtpzf'
app.config['MYSQL_PASSWORD'] = 'wibpgq8uv06eciat'
app.config['MYSQL_DB'] = 'fwtyv7la1cjn796i'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MySQL
mysql = MySQL(app)


# WRAPS
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized access to the page.', 'danger')
            return redirect(url_for('login'))

    return wrap


def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('You are already logged in!', 'danger')
            return redirect(url_for('dashboard'))

    return wrap


# ROUTES
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
    result = cur.execute("SELECT * FROM articles_")

    articles = cur.fetchall()

    for ar in articles:
        ar['body'] = Markup(ar['body'])

    cur.close()

    return render_template('articles.html', articles=articles)


# Article page
@app.route('/articles/<string:id>/')
def article(id):
    # connect to db & get article info
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    return render_template('article.html', article=article)


# Support page
@app.route('/support')
def support():
    return render_template('support.html')


# Registration
@app.route('/register', methods=['GET', 'POST'])
@is_not_logged_in
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

        # checking if user email or username already exists
        result = cur.execute("SELECT * FROM users_ WHERE email=%s OR username=%s", [email, username])
        if result > 0:
            flash("This email address or username is already taken.", "danger")
            return redirect(url_for("register"))

        else:
            # submit to DB
            cur.execute("INSERT INTO users_ (name,email,username,password) VALUES (%s, %s, %s, %s)",
                        (name, email, username, password))

            # commit changes & close connection
            mysql.connection.commit()
            cur.close()

            flash("You are now registered and can log in!", "success")
            return redirect(url_for("login"))

    else:
        return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
@is_not_logged_in
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form['email']
        password_candidate = request.form['password']

        # creating cursor
        cur = mysql.connection.cursor()

        # submit to DB & close connection
        result = cur.execute("SELECT * FROM users_ WHERE email = %s OR username = %s", [username, username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # compare passwrds
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = data['username']
                if (data['username'] in app.config['ADMIN_LIST']):
                    session['admin'] = True
                    flash("Welcome administrator %s. Glad to see you back!" % data['username'], "success")
                else:
                    flash("You are now logged in!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("The username or password didn't match!", "danger")
        else:
            flash("The username or password didn't match", "danger")

        cur.close()
    return render_template('login.html', form=form)


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # connect to db & get articles
    cur = mysql.connection.cursor()

    try:
        if(session['admin']):
            cur.execute("SELECT * FROM articles_");
    except:
        cur.execute("SELECT * FROM articles_ where author=%s", [session['username']])

    articles = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', articles=articles)


# Add article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)

    if (request.method == 'POST' and form.validate()):
        title = form.title.data
        body = form.body.data

        # database logic
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles_(title,body,author) VALUES (%s,%s,%s)", (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('New article successfully created!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


# Edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    form = ArticleForm(request.form)

    if (request.method == 'POST' and form.validate()):
        title = form.title.data
        body = form.body.data

        # database logic
        cur = mysql.connection.cursor()
        cur.execute("UPDATE articles_ SET title=%s, body=%s WHERE id=%s", (title, body, [id]))
        mysql.connection.commit()
        cur.close()

        flash('Article successfully edited!', 'success')
        return redirect(url_for('dashboard'))
    elif (request.method == "GET"):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])
        article = cur.fetchone()
        cur.close()

        form.title.data = article['title']
        form.body.data = article['body']

        return render_template('edit_article.html', form=form)


@app.route('/delete_article/<string:id>/')
@is_logged_in
def delete_article(id):
    # database logic
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles_ WHERE id=%s and author = %s", (id, session['username']))
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


# Privacy
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


# ERRORS
# 404
@app.errorhandler(404)
def error_404(req):
    app.logger.info(req)
    return make_response(render_template("error/404.html"), 404)


@app.errorhandler(400)
def bad_request(req):
    app.logger.info(req)
    return make_response(render_template("error/400.html"), 400)


@app.errorhandler(500)
def server_error(req):
    app.logger.info(req)
    return make_response(render_template("error/500.html"), 500)

#PROCESSORS
@app.context_processor
def utility_processor():
    def article_body(string):
        i1 = string.find('<p>')
        i2 = string.find('</p>')
        output = ''

        if(i1 != -1 and i2 != -1):
            output += string[int(i1)+3:int(i2)]

        if len(output) > 300:
            output = output[0:300] + '...'

        return output
    return dict(article_body=article_body)


# running the application
if __name__ == '__main__':
    app.run(debug=True)

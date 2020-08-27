from flasky import app, mail
from flask import render_template, Markup, request, flash, redirect, url_for, session
from flask_mail import Message
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flasky.WTFormClasses import RegisterForm, LoginForm, ArticleForm
from flasky.wraps import is_not_logged_in, is_logged_in
from flasky.helpers import create_activation_link, decrypt_activation_link, activation_mail_body, allowed_file
from werkzeug.utils import secure_filename
import os
import secrets

# init MySQL
mysql = MySQL(app)


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

            # commit changes
            mysql.connection.commit()

            # getting user id & creating activation link
            cur.execute("SELECT id FROM users_ WHERE username = %s", [username])
            user = cur.fetchone()
            activation_link = create_activation_link(str(user['id']))

            # sending mail with activation link
            msg = Message("Your Flasky-App account activation link",
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.html = activation_mail_body(username, request.url_root, activation_link)
            try:
                mail.send(msg)
            except:
                app.logger.info('Failed to send mail; check your SMTP connexion')

            # close connection
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
                session['activated'] = data['activated']
                if (data['username'] in app.config['ADMIN_LIST'] or data['email'] in app.config['ADMIN_LIST']):
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

# Activating account
@app.route('/activate')
def activate():
    link = request.args.get('link')
    id = decrypt_activation_link(link)

    if(id == -1):
        flash("Invalid activation link!", "danger")
        return redirect(url_for("index"))

    # creating cursor
    cur = mysql.connection.cursor()

    # setting user as activated
    cur.execute("UPDATE users_ SET activated = '1' WHERE (id = %s);", [id])
    mysql.connection.commit()

    # getting user details for creating a logging session
    result = cur.execute("SELECT * FROM users_ WHERE id = %s", [id])

    if result > 0:
        data = cur.fetchone()

        session['logged_in'] = True
        session['username'] = data['username']
        session['activated'] = data['activated']

        if (data['username'] in app.config['ADMIN_LIST'] or data['email'] in app.config['ADMIN_LIST']):
            session['admin'] = True
            if data['activated']:
                flash("Your account is already activated!", "warning")
            else:
                flash("Welcome administrator %s. Glad to see you back! Ur activated too!" % data['username'], "success")
        else:
            if data['activated']:
                flash("Your account is already activated!", "warning")
            else:
                flash("Your account have been activated successfully!", "success")
    else:
        flash("Your account could not be found", "danger")
        return redirect(url_for("index"))

    return redirect(url_for("dashboard"))

# Sending activation link
@app.route('/send_activation')
@is_logged_in
def send_activation():
    username = session['username']

    # creating cursor
    cur = mysql.connection.cursor()

    # getting user id & email
    result = cur.execute("SELECT id,email FROM users_ WHERE username = %s", [username])

    if result > 0:
        data = cur.fetchone()

        email = data['email']
        id = data['id']
        activation_link = create_activation_link(str(id))

        msg = Message("Your Flasky-App account activation link",
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])

        msg.html = activation_mail_body(username, request.url_root, activation_link)
        try:
            mail.send(msg)
        except:
            app.logger.info('Failed to send mail; check your SMTP connexion')

        flash("The activation link was sent successfully to %s!" % email, "success")
    else:
        flash("Failed to create the activation link", "danger")

    return redirect(url_for("dashboard"))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # connect to db & get articles
    cur = mysql.connection.cursor()

    try:
        if (session['admin']):
            cur.execute("SELECT * FROM articles_")
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

    if request.method == 'POST' and form.validate():
        #receiving text data from form
        title = form.title.data
        body = form.body.data
        file = request.files['image']

        # checking for valid file
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secrets.token_hex(20) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = "INSERT INTO articles_(title,body,author,image) VALUES (%s,%s,%s, %s)"
            query_args = (title, body, session['username'], filename)
        else:
            query = "INSERT INTO articles_(title,body,author) VALUES (%s,%s,%s)"
            query_args = (title, body, session['username'])

        # database logic
        cur = mysql.connection.cursor()
        cur.execute(query, query_args)
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

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # database logic
        cur = mysql.connection.cursor()
        cur.execute("UPDATE articles_ SET title=%s, body=%s WHERE id=%s", (title, body, [id]))
        mysql.connection.commit()
        cur.close()

        flash('Article successfully edited!', 'success')
        return redirect(url_for('article', id=id))
    elif request.method == "GET":
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

    flash('The article with id %s was successfully deleted!' % id, 'success')
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

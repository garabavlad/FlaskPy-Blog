from flasky import app, mail
from flask import render_template, abort, request, flash, redirect, url_for, session, jsonify
from flask_mail import Message
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flasky.WTFormClasses import RegisterForm, LoginForm, ArticleForm
from flasky.middleware import is_not_logged_in, is_logged_in, is_admin
from flasky.helpers import create_activation_link, decrypt_activation_link, activation_mail_body, allowed_file
from flasky.config import oauth, google
import os
import secrets
import stripe

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
    cur.execute("SELECT * FROM articles_ WHERE deleted=0")

    articles = cur.fetchall()

    for ar in articles:
        ar['create_date'] = ar['create_date'].strftime("%b %d %Y")

    cur.close()

    return render_template('articles/articles.html', articles=articles)


# Article page
@app.route('/articles/<string:id>/')
def article(id):
    # connect to db & get article info
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])

    if res:
        article = cur.fetchone()
        article['create_date'] = article['create_date'].strftime("%b %d %Y")

        if article['deleted'] == b'1':
            flash("The requested article is in the trash", "danger")
    else:
        flash("The requested article is not available", "danger")
        return redirect(url_for("articles"))

    cur.close()
    return render_template('articles/article.html', article=article)


# Add article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        # receiving text data from form
        title = form.title.data
        body = form.body.data
        file = request.files['image']

        # checking for valid file
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secrets.token_hex(20) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = "INSERT INTO articles_(title,body,author,image) VALUES (%s,%s,%s, %s)"
            query_args = (title, body, session['auth']['username'], filename)
        else:
            query = "INSERT INTO articles_(title,body,author) VALUES (%s,%s,%s)"
            query_args = (title, body, session['auth']['username'])

        # database logic
        cur = mysql.connection.cursor()
        cur.execute(query, query_args)
        mysql.connection.commit()
        cur.close()

        flash('New article created successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('articles/add_article.html', form=form)


# Edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        file = request.files['image']

        # checking for valid file
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secrets.token_hex(20) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = "UPDATE articles_ SET title=%s, body=%s, image=%s WHERE id=%s"
            query_args = (title, body, filename, [id])
        else:
            query = "UPDATE articles_ SET title=%s, body=%s WHERE id=%s"
            query_args = (title, body, [id])

        # database logic
        cur = mysql.connection.cursor()
        cur.execute(query, query_args)
        mysql.connection.commit()
        cur.close()

        flash('Article successfully edited!', 'success')
        return redirect(url_for('article', id=id))

    elif request.method == "GET":
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])

        if res:  # checking if article is not deleted
            article = cur.fetchone()
            article['create_date'] = article['create_date'].strftime("%b %d %Y")

            if article['deleted'] == b'1':
                flash("The requested article is in the trash", "danger")
        else:
            flash("The requested article is not available", "danger")
            return redirect(url_for("articles"))

        form.title.data = article['title']
        form.body.data = article['body']

        cur.close()
        return render_template('articles/edit_article.html', form=form)


# Deleting articles
@app.route('/delete_article/<string:id>/')
@is_logged_in
def delete_article(id):
    # database logic
    cur = mysql.connection.cursor()
    # request from a non admin user; have to check if he's the author
    cur.execute("UPDATE articles_ SET deleted=%s WHERE id=%s and author=%s", (1, id, session['auth']['username']))

    mysql.connection.commit()
    cur.close()

    flash('The article with id %s was successfully deleted!' % id, 'success')
    return redirect(url_for('dashboard'))


# Returning articles
@app.route('/return_article/<string:id>/')
@is_logged_in
def return_article(id):
    # database logic
    cur = mysql.connection.cursor()
    # request from a non admin user; have to check if he's the author
    cur.execute("UPDATE articles_ SET deleted=%s WHERE id=%s and author=%s", (0, id, session['auth']['username']))

    mysql.connection.commit()
    cur.close()

    flash('The article with id %s was moved out of the trash successfully!' % id, 'success')
    return redirect(url_for('dashboard'))


# Returns a raw article page for iframes
@app.route('/raw/articles/<string:id>/')
@is_admin
def raw_article(id):
    # connect to db & get article info
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])

    article = cur.fetchone()
    article['create_date'] = article['create_date'].strftime("%b %d %Y")
    cur.close()
    return render_template('articles/raw_article.html', article=article)


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
        return render_template('auth/register.html', form=form)


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
                # passwords matched so create an auth session
                session['auth'] = {}
                session['auth']['username'] = data['username']
                session['auth']['email'] = data['email']
                session['auth']['activated'] = data['activated']
                if (data['username'] in app.config['ADMIN_LIST'] or data['email'] in app.config['ADMIN_LIST']):
                    # checking if username or email is in admin list
                    session['auth']['admin'] = True
                    flash("Welcome administrator %s. Glad to see you back!" % data['username'], "success")
                else:
                    flash("You are now logged in!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("The username or password didn't match!", "danger")
        else:
            flash("The username or password didn't match", "danger")

        cur.close()
    return render_template('auth/login.html', form=form)

# Forgot password
@app.route('/iforgot')
def iforgot():
    return render_template('auth/forgot-password.html')

# PAssword recoved
@app.route('/recover')
def recover():
    return render_template('auth/recover-password.html')


# OAuth Google login
@app.route('/google/login')
@is_not_logged_in
def google_login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('google_authorize', _external=True)  # redirecting user to google auth
    return google.authorize_redirect(redirect_uri)


# OAuth Google authorize
@app.route('/google/authorize')
@is_not_logged_in
def google_authorize():
    google = oauth.create_client('google')  # google oauth client
    token = google.authorize_access_token()  # getting google authorization token
    resp = google.get('userinfo', token=token)  # getting user info
    user_info = resp.json()

    # getting values from Google OAUTH API
    name = user_info['name']
    email = user_info['email']

    # checking if user exists in db
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users_ WHERE email=%s", [email])
    if result > 0:  # the user is in db
        data = cur.fetchone()
        username = data['username']

    else:  # creating new user in db

        # generating an username and password
        username = user_info['given_name'] + '.' + user_info['family_name'] + '.' + secrets.token_hex(2)
        password = sha256_crypt.encrypt(str(secrets.token_hex(10)))

        # inserting new user to DB
        cur.execute("INSERT INTO users_ (name,email,username,password) VALUES (%s, %s, %s, %s)",
                    (name, email, username, password))
        mysql.connection.commit()

    # creating auth session
    session['auth'] = {}
    session['auth']['username'] = username
    session['auth']['activated'] = 0  # user is not activated
    session['auth']['email'] = email

    # checking if email is in admin list
    if username in app.config['ADMIN_LIST'] or email in app.config['ADMIN_LIST']:
        session['auth']['admin'] = True
        flash("Welcome administrator %s. Glad to see you back!" % username, "success")
    else:
        flash("You have logged in successfully!", "success")

    cur.close()
    return redirect('/dashboard')


# Logout
@app.route('/logout')
def logout():
    if 'auth' in session: session.pop('auth')
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('index'))


# Become admin
@app.route('/become_admin')
def become_admin():
    if 'auth' in session:
        session['auth']['admin'] = True
        flash('You just became an administrator, congrats!', 'info')

    return redirect('/dashboard')


# Become user
@app.route('/become_user')
def become_user():
    if 'auth' in session and 'admin' in session['auth']:
        session['auth'].pop('admin')
        flash('You just became an user!', 'info')

    return redirect('/dashboard')


# Activating account
@app.route('/activate')
def activate():
    link = request.args.get('link')
    id = decrypt_activation_link(link)

    if (id == -1):
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

        session['auth'] = {}
        session['auth']['username'] = data['username']
        session['auth']['activated'] = data['activated']
        session['auth']['email'] = data['email']

        if (data['username'] in app.config['ADMIN_LIST'] or data['email'] in app.config['ADMIN_LIST']):
            session['auth']['admin'] = True
            flash("Welcome administrator %s. Glad to see you back! Ur activated too!" % data['username'], "success")
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
    username = session['auth']['username']

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


# ADMINISTRATION
# Admin Dashboard
@app.route('/admin/dashboard')
@is_logged_in
@is_admin
def admin_dashboard():
    return render_template('adminLTE/dashboard.html')


@app.route('/admin/dashboard/articles')
@is_logged_in
@is_admin
def admin_dashboard_articles():
    get_show = request.args.get("show")

    # connecting to db and getting articles
    cur = mysql.connection.cursor()
    if get_show == 'trashed':
        cur.execute("SELECT * FROM articles_ WHERE deleted = 1")
        trashed = 1
    else:
        cur.execute("SELECT * FROM articles_ WHERE deleted = 0")
        trashed = 0

    articles = cur.fetchall()

    for ar in articles:
        ar['create_date'] = ar['create_date'].strftime("%b %d %Y")

    cur.close()
    return render_template('adminLTE/articles.html', articles=articles, trashed=trashed)


@app.route('/admin/dashboard/articles/<string:id>')
@is_logged_in
@is_admin
def admin_dashboard_articles_article(id):
    return render_template('adminLTE/article.html', id=id)


@app.route('/admin/dashboard/articles/new', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def admin_dashboard_article_new():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        file = request.files['image']

        # checking for valid file
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secrets.token_hex(20) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = "INSERT INTO articles_(title,body,author,image) VALUES (%s,%s,%s, %s)"
            query_args = (title, body, session['auth']['username'], filename)
        else:
            query = "INSERT INTO articles_(title,body,author) VALUES (%s,%s,%s)"
            query_args = (title, body, session['auth']['username'])

        cur = mysql.connection.cursor()
        cur.execute(query, query_args)
        mysql.connection.commit()
        cur.close()

        flash('New article created successfully.', 'success')
        return redirect(url_for('admin_dashboard_articles'))

    return render_template('adminLTE/add_article.html', form=form)


@app.route('/admin/dashboard/articles/edit/<string:id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def admin_dashboard_article_edit(id):
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        file = request.files['image']

        # checking for valid file
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secrets.token_hex(20) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = "UPDATE articles_ SET title=%s, body=%s, image=%s WHERE id=%s"
            query_args = (title, body, filename, [id])
        else:
            query = "UPDATE articles_ SET title=%s, body=%s WHERE id=%s"
            query_args = (title, body, [id])

        cur = mysql.connection.cursor()
        cur.execute(query, query_args)
        mysql.connection.commit()
        cur.close()

        flash('Article edited successfully', 'success')
        return redirect(url_for('admin_dashboard_articles'))
    elif request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM articles_ WHERE id = %s", [id])
        article = cur.fetchone()
        cur.close()

        form.title.data = article['title']
        form.body.data = article['body']

        return render_template('adminLTE/edit_article.html', form=form)


@app.route('/admin/dashboard/articles/delete/<string:id>')
@is_logged_in
@is_admin
def admin_dashboard_articles_delete(id):
    cur = mysql.connection.cursor()

    cur.execute("UPDATE articles_ SET deleted=%s WHERE id=%s", (1, [id]))

    mysql.connection.commit()
    cur.close()

    flash('The article with id %s was successfully deleted!' % id, 'success')

    return redirect(url_for('admin_dashboard_articles'))


@app.route('/admin/dashboard/articles/return/<string:id>')
@is_logged_in
@is_admin
def admin_dashboard_articles_return(id):
    cur = mysql.connection.cursor()

    cur.execute("UPDATE articles_ SET deleted=%s WHERE id=%s", (0, [id]))

    mysql.connection.commit()
    cur.close()

    flash('The article with id %s was moved out of the trash successfully!' % id, 'success')

    return redirect(url_for('admin_dashboard_articles'))


# User Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # connect to db & get articles
    cur = mysql.connection.cursor()

    try:
        if (session['auth']['admin']):
            cur.execute("SELECT * FROM articles_ WHERE deleted = 0")
    except:
        cur.execute("SELECT * FROM articles_ WHERE author=%s AND deleted = 0", [session['auth']['username']])

    articles = cur.fetchall()
    cur.close()

    for ar in articles:
        ar['create_date'] = ar['create_date'].strftime("%b %d %Y")

    return render_template('dashboard.html', articles=articles)


# Privacy
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


# Payments
# Payment page
@app.route('/payment')
def payment():
    return render_template('payment.html')


# Successful payment page
@app.route('/success_payment')
def success_payment():
    session_id = request.args.get('session_id')

    if session_id == None:
        flash("Unauthorized request", "danger")
        return redirect(url_for("index"))

    # Retrieving data from stripe API
    try:
        ssn = stripe.checkout.Session.retrieve(session_id)
    except:
        flash("Invalid Session ID", "danger")
        return redirect(url_for("index"))

    cst = stripe.Customer.retrieve(ssn.customer)

    return render_template('success_payment.html', customer=cst.email)


# Checkout page
@app.route('/checkout_session', methods=['POST'])
def checkout_session():
    chkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'A little donation',
                },
                'unit_amount': 1000,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('success_payment', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('payment', _external=True)
    )

    return jsonify({'id': chkout_session.id, 'pk': app.config['STRIPE_PUBLISHABLE_KEY']})

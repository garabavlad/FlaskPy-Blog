from functools import wraps
from flask import flash, redirect, url_for, session


# WRAPS
# MWare for checking if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'auth' in session and 'username' in session['auth']:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized access to the page.', 'danger')
            return redirect(url_for('login'))
    return wrap


# MWare for checking if user is not logged in
def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'auth' not in session:
            return f(*args, **kwargs)
        else:
            flash('You are already logged in!', 'danger')
            return redirect(url_for('dashboard'))
    return wrap


# MWare for checking if the user is an administrator
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'auth' in session and 'admin' in session['auth'] and session['auth']['admin']==True:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized access to the page. You need to have administrator privileges!', 'danger')
            return redirect(url_for('dashboard'))
    return wrap
from functools import wraps
from flask import flash, redirect, url_for, session


# WRAPS
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'auth' in session and 'username' in session['auth']:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized access to the page.', 'danger')
            return redirect(url_for('login'))

    return wrap


def is_not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'auth' not in session:
            return f(*args, **kwargs)
        else:
            flash('You are already logged in!', 'danger')
            return redirect(url_for('dashboard'))

    return wrap
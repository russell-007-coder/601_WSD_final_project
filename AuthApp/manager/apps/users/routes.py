from flask import Blueprint, redirect, request, flash, url_for, render_template, current_app
from flask_login import login_required, login_user, current_user, logout_user
from functools import wraps

from manager.models import Users
from manager.ext import csrf, db

from manager.apps.users import users

from manager.models import Users
from manager.apps.users.forms import LoginForm, BeginPasswordResetForm, PasswordResetForm, SignupForm
from manager.apps.users.forms import UpdateCredentials, SendEmailAgainForm

from manager.libs.mail import send_email


def anonymous_required(url='/'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('You do not have permission to do that.', 'danger')
                return redirect('/')

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@users.route("/", methods=['GET'])
def home():
    if not current_user.is_authenticated:
        flash("You need to login first.", 'info')
        return redirect(url_for('users.login'))
    if not current_user.verified:
        flash('You need to verify youself first', 'success')
        return redirect(url_for('users.verify', user_id=current_user.id))
    return render_template('home.html')


@users.route("/user/<user_id>", methods=['GET'])
def user(user_id):
    user = Users.query.get(user_id)
    if user:
        return "User"
    return "No User with this ID"


@users.route('/login', methods=['GET','POST'])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get('next'))
    if form.validate_on_submit():
        u = Users.find_by_identity(form.identity.data)
        if u and u.authenticated(password=form.password.data):
            login_user(u)
            u.is_active(True)
            u.update_activity_tracking(request.remote_addr)
            return redirect(url_for('users.home'))
        else:
            flash('Identity or password is incorrect.', 'danger')
    return render_template('login.html', form=form)


@users.route('/register', methods=['GET','POST'])
@anonymous_required()
def register():
    form = SignupForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data.lower(),
                     password = form.password.data,
                     email=form.email.data.lower())
        db.session.add(user)
        db.session.commit()
        if login_user(user):
            user.update_activity_tracking(request.remote_addr)
            flash('Welcome, You are Registered Succesfully.', 'success')
            send_verification_email(user.id)
            return redirect(url_for('users.verify', user_id=user.id))
    return render_template('register.html', form=form)


def send_verification_email(user_id):
    user = Users.query.get(user_id)
    confirm_url = url_for('users.verification_link', user_id=user_id, _external=True)
    html = render_template('mails/confirm_email.html', username=user.username, confirm_url=confirm_url)
    send_email(to= user.email, subject= 'Email Confirmation',template=html)
    flash('We have send you an email please check.', 'secondary')
    return True

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.home'))


@users.route("/send-again/<user_id>")
def send_again(user_id):
    user = Users.query.get(user_id)
    send_verification_email(user.id)
    return redirect(url_for('users.verify', user_id=user_id))

@users.route("/verify/<user_id>")
def verify(user_id):
    user = Users.query.get(user_id)
    return render_template('verify.html', user=user)


@users.route('/verification-link/<user_id>', methods=['GET', 'POST'])
def verification_link(user_id):
    user = Users.query.get(user_id)
    if user.verified:
        flash('Your account is already verified.', 'success')
        return redirect(url_for('users.home'))
    else:
        user.verified = True
        db.session.commit()
        flash('You have confirmed your account. Thank you, for your coopreation.', 'success')
    return redirect(url_for('users.home'))
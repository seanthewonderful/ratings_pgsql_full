"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"
WTF_CSRF_SECRET_KEY = 'a random string'
# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]=False



class RegisterForm(FlaskForm):
    email = EmailField('email', render_kw={'placeholder':"Email Address"}, validators=[DataRequired()])
    password = PasswordField('password', render_kw={'placeholder':"Password"}, validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index(user):
    """Homepage."""
    if user in session:
        return render_template('homepage.html', user=user)
    return render_template('homepage.html')


@app.route('/users')
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/login')
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(form.email.data).one()
        if user.password == form.password.data:
            session[user.user_id] = user
            return render_template('homepage.html', user=user)
        else: 
            return redirect(url_for('login'))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.email.data)
        if User.query.filter_by(email=form.email.data).first():
            return redirect(url_for('register'))
        else:
            user = User(email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            return render_template('profile.html', user=user)
    return render_template('register.html', form=form)


@app.route('/profile')
def profile(user):
    return render_template('profile.html', user=user)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

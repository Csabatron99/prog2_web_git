


from flask import Flask, render_template, request, url_for, redirect, flash
from sentry_sdk.integrations.flask import FlaskIntegration

import sentry_sdk

from wtforms import Form, TextField, validators, PasswordField
from passlib.hash import sha256_crypt

from MySQLdb import Connection, escape_string as thwart

from .content_management import Content
from .dbconnect import connection_db

TOPIC_DICT = Content()

sentry_sdk.init(
    dsn="https://93c0ddd2b5a84a708bb1b7ea01836841@o427051.ingest.sentry.io/5806504",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0
)

app = Flask(__name__)

@app.route('/debug-sentry/')
def trigger_error():
    division_by_zero = 1 / 0

    
    

class RegistrationForm(Form):
    fname = TextField('inputFName', [validators.InputRequired()])
    
    lname = TextField('inputLName', [validators.InputRequired()])
    
    username = TextField('inputUsername', [validators.InputRequired()])
    
    email1 = TextField('inputEmail1', [validators.Email(), validators.InputRequired(), validators.EqualTo('email2', message='Email must match')])
    
    email2 = TextField('inputEmail2', [validators.Email(), validators.InputRequired()])
    
    password1 = PasswordField('inputPassword1', [validators.InputRequired(), validators.EqualTo('password2', message='Passwords must match')])
    
    password2 = PasswordField('inputPassword2', [validators.InputRequired()])
    
    regcode = PasswordField('inputRegistrationCode', [validators.InputRequired()])

@app.route('/')
def homepage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)

@app.route('/about/')
def about():
    try:
        return render_template("about.html", TOPIC_DICT = TOPIC_DICT)
    except Exception as e:
        return(str(e))


@app.route('/login/', methods = ['GET','POST'])
def login():
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']

            if attempted_username == "admin" and attempted_password == "alma":
                return redirect(url_for('about'))
            else:
                return render_template("login.html")
        return render_template("login.html")
    except Exception as e:
        return render_template("login.html")



@app.route('/register/', methods=["GET","POST"])
def register():
    try:
        form = RegistrationForm(request.form)
        
        if request.method == "POST" and form.validate():
            fname = form.fname.data
            lname = form.lname.data
            username = form.username.data
            email = form.email1.data
            password = sha256_crypt.hash((str(form.password1.data)))
            c, conn = connection_db()
            x = c.excute("SELECT * FROM users WHERE username= (%s)", (thwart(username)))
            if int(x) > 0:
                flash("This username is alredy used in the system")
                return render_template("register.html", form=form)
           
        return render_template("register.html")
    except Exception as e:
        return render_template("500.html", error = e)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html", error = e)


if __name__ == "__main__":
    app.run()

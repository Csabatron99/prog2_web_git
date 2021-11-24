
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash, session
from functools import wraps

from wtforms import Form, StringField, validators, PasswordField
from passlib.hash import sha256_crypt
import gc

from MySQLdb import Connection, escape_string as thwart

from .content_management import Content
from .dbconnect import connection_db

TOPIC_DICT = Content()

app = Flask(__name__)

headings = ("Name", "Role", "Salary", "Egyik", "Masik")
data = (
        ("Alma","Korte","Cukor","kutya","cica"),
        ("Alma","Korte","Cukor","kutya","cica"),
        ("Alma","Korte","Cukor","kutya","cica"),
        ("Alma","Korte","Cukor","kutya","cica"), 
       )

class LoginForm(Form):
    username = StringField('inputUsernameL', [validators.DataRequired()])
    
    password1 = PasswordField('inputPassword1L', [validators.DataRequired()])

class RegistrationForm(Form):
    fname = StringField('inputFName', [validators.DataRequired()])
    
    lname = StringField('inputLName', [validators.DataRequired()])
    
    username = StringField('inputUsername', [validators.DataRequired()])
    
    email1 = StringField('inputEmail1', [validators.Email(), validators.DataRequired(), validators.EqualTo('email2', message='Email must match')])
    
    email2 = StringField('inputEmail2', [validators.Email(), validators.DataRequired()])
    
    phoneW = StringField('inputPhoneNumber1' , [validators.DataRequired()])
    
    phoneP = StringField('inputPhoneNumber2', [validators.DataRequired()])
    
    location = StringField('inputLocation', [validators.NoneOf('Select one location.', message='Pease select one location')])

    role = StringField('inputRole', [validators.NoneOf('Select one role.', message='Select one please.')])
    
    password1 = PasswordField('inputPassword1', [validators.DataRequired(), validators.EqualTo('password2', message='Passwords must match')])
    
    password2 = PasswordField('inputPassword2', [validators.DataRequired()])
    
    regcode = PasswordField('inputRegistrationCode', [validators.DataRequired()])
    
class C_P_Form(Form):
    tip = StringField('tipStringIN', [validators.DataRequired()])
    

@app.route('/')
def homepage():
    try:
        return render_template("index.html")
    except Exception as e:
        return str(e)





def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap


@app.route('/c_p/')
@login_required
def c_p():
    try:
        formCP = C_P_Form(request.form)
        return render_template("c_p.html", TOPIC_DICT = TOPIC_DICT, form = formCP, headings = headings, data=data)
    except Exception as e:
        return(str(e))

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("logged out")
    gc.collect()
    return redirect(url_for('homepage'))

@app.route('/login/', methods = ["GET","POST"])
def login():
    error = ''
    try:
        c1, conn1 = connection_db()
        formL = LoginForm(request.form)
        if request.method == "POST":
            querry = "SELECT * FROM `workers` WHERE `Username` = (%s)"
            value = (request.form['username'],)
            
            data = c1.execute(querry, value)
            data = c1.fetchone() [4]
            if sha256_crypt.verify(request.form['password'],data) == True:
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You logged in oniichan")
                return redirect(url_for('c_p'))
            else:
                error = "Invalid credentials, try again"
                
        gc.collect()
        return render_template("login.html", error=error)
    except Exception as e:
        return render_template("login.html", error=e)


@app.route('/register/', methods=["GET","POST"])
def register():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            fnameR = form.fname.data
            lnameR = form.lname.data
            usernameR = form.username.data
            emailR = form.email1.data
            phoneWR = form.phoneW.data
            phonePR = form.phoneP.data
            locationR = form.location.data
            roleR = form.role.data
            passwordR = sha256_crypt.hash((str(form.password1.data)))
            regcodeR = form.regcode.data
            c1, conn1 = connection_db()
            
            usernameR = usernameR.strip()
            cquerry = "SELECT * FROM `workers` WHERE `Username` = (%s)"
            cvalue = (usernameR,)
            c1.execute(cquerry, cvalue)
            c1.fetchall()
            a = c1.rowcount
            if int(a) > 0:
                flash("This username is alredy used in the system")
                return render_template("register.html", form=form)
            else: 
                querri = "INSERT INTO workers (Prenume, Nume, Username, Password, Role, Telefon_1, Telefon_2, Email_1, Email_2, Location, Link_For_Contract) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (fnameR, lnameR, usernameR, passwordR, roleR, phoneWR, phonePR, usernameR+"@tikvahome.ro", emailR, locationR, "TEST" )
                
                c1.execute(querri,values)
                conn1.commit() 
                flash("TY for registering oniichan")
                c1.close()
                conn1.close()
                gc.collect()
                session['logged_in'] = True
                session['username'] = usernameR
                return redirect(url_for('login'))
        return render_template("register.html", form = form)
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

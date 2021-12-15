
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash, session
from functools import wraps

from wtforms import Form, StringField, validators, PasswordField, SelectField
from passlib.hash import sha256_crypt
import gc

#from MySQLdb import Connection, escape_string as thwart

from .content_management import Content
from .dbconnect import connection_db, connection_rp

TOPIC_DICT = Content()

app = Flask(__name__)
headings1 = ("Prenume", "Nume", "Username", "Role", "Telefon 1", "Telefon 2", "Email 1", "Email 2", "Location")
headings11 = ("ID","Prenume", "Nume", "Username", "Password", "Role", "Telefon_1", "Telefon_2", "Email_1", "Email_2", "Location", "Link_For_Contract")
headings2 = ("ID","Prenume", "Nume", "CNP", "Születési év", "Hely", "Telefon", "Email", "Családi állapot")

#data = (
#        ("Alma","Korte","Cukor","kutya","cica"),
#        ("Alma","Korte","Cukor","kutya","cica"),
#        ("Alma","Korte","Cukor","kutya","cica"),
#        ("Alma","Korte","Cukor","kutya","cica"), 
#       )




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
    
class C_P_Form_ADD(Form):
    vnev = StringField('inputVezetéknév', [validators.DataRequired()])
    
    knev = StringField('inputKeresztnév', [validators.DataRequired()])

    szsz = StringField('inputSZSZ', [validators.DataRequired()])

    sze = StringField('inputSZE', [validators.DataRequired()])

    lak = StringField('inputLakhely', [validators.DataRequired()])

    tel = StringField('inputTelefon', [validators.DataRequired()])

    email = StringField('inputEmail', [validators.Email(), validators.DataRequired()])
    
    csa = SelectField('inputCSA',  choices=[("Egyedülálló"),("Házas"),("Eljegyzett")])

class C_P_Form_SEARCH(Form):
    Svnev = StringField('inputVezetéknév')
    
    Sknev = StringField('inputKeresztnév')

    Sszsz = StringField('inputSZSZ')

    Ssze = StringField('inputSZE')

    Slak = StringField('inputLakhely')

    Stel = StringField('inputTelefon')

    Semail = StringField('inputEmail')

class C_P_Form_REM(Form):
    id = StringField('inputId', [validators.DataRequired()])

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


@app.route('/c_p/', methods=('GET', 'POST'))
@login_required
def c_p():
    try:
        c2, conn2 = connection_rp()
        c1,conn1 = connection_db()
        formAdd = C_P_Form_ADD(request.form)
        formRem = C_P_Form_REM(request.form)
        formSearch = C_P_Form_SEARCH(request.form)
        
        if request.method == "POST":
            if request.form.get("Add_bt") and formAdd.validate():
                vnev = formAdd.vnev.data
                knev = formAdd.knev.data
                szsz = formAdd.szsz.data
                sze = formAdd.sze.data
                lak = formAdd.lak.data
                tel = formAdd.tel.data
                email = formAdd.email.data
                csa = formAdd.csa.data
                querri = "INSERT INTO customer (Prenume, Nume, CNP, Szul, Location, Telefon, Email, Csal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (vnev, knev, szsz, sze, lak, tel, email, csa)
                c2.execute(querri,values)
                conn2.commit()
                return redirect(url_for('c_p'))
            elif request.form.get("Remove_bt") and formRem.validate():
                id = formRem.id.data
                querri = "DELETE FROM customer WHERE ID_Cus = "+id
                c2.execute(querri)
                conn2.commit()
                return redirect(url_for('c_p'))
            elif request.form.get("Search_bt"):
                Sszsz = formSearch.Sszsz.data 
                c2.execute("SELECT * FROM customer WHERE CNP = "+ Sszsz )
                datatoshow2 = c2.fetchall()
                return render_template("c_p.html", TOPIC_DICT = TOPIC_DICT, formAdd = formAdd, formRem = formRem, formSearch = formSearch, headings1 = headings1, headings2 = headings2, data2=datatoshow2)
        c1.execute("SELECT * FROM `workers` where Username = '"+ session['username'] +"'")
        datatoshow1 = c1.fetchall()
        c2.execute("SELECT * FROM `customer`")
        datatoshow2 = c2.fetchall()
        return render_template("c_p.html", TOPIC_DICT = TOPIC_DICT, formAdd = formAdd, formRem = formRem, formSearch = formSearch , headings1 = headings1, headings2 = headings2, data1=datatoshow1, data2=datatoshow2)
    except Exception as e:
        return(str(e))

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("Logged out")
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
            a = c1.rowcount
            data = c1.fetchone() [4]
            if sha256_crypt.verify(request.form['password'],data) == True or int(a) > 0:
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You are logged in. Dont forget to log out!")
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
                flash("Registration was succesfull. Please log in.")
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

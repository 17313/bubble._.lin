
from flask import Flask, render_template, g , request, redirect, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DATABASE = 'Bubble._.Lin.db'
global admin
admin = False
global user_id
user_id = None
global username
username = 


app.secret_key = 'bubbles'


def get_db():
    '''get database'''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    '''closes connection to database'''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    return

def get_user():
    if session.get("user"):
        '''get user from database'''
        user = "SELECT username FROM drink_order WHERE id =?"
        cursor = get_db().cursor()
        cursor.execute(user)
        username = cursor.fetch(1)
        pass
    return False

@app.route('/')
def index():
    '''make an app route and link to index html template'''
    return render_template('index.html')




@app.route('/signup', methods=["GET", "POST"])
def signup():
    '''sign up and insert information into database'''
    if request.method == "GET" :
        return render_template("signup.html")
    error=None
    cursor = get_db().cursor()
    new_username = request.form["username"]
    new_password = request.form["password"]
    if new_username == "" or new_password == "":
        error = "Please enter a username and a password"
        return render_template("signup.html", error=error)
    sql_query = "SELECT username FROM login WHERE username = ?"
    cursor.execute(sql_query, (new_username,))
    if bool(cursor.fetchall()):
        error = "Username already taken. Please try again"
        return render_template("signup.html", error=error)
    sql_query = "INSERT INTO login (username, password) VALUES (?,?)"
    '''insert new username and password into database'''
    cursor.execute(sql_query, (new_username, generate_password_hash(new_password, )))
    get_db().commit()
    return redirect("/")
    

# find and use code from database to access user functions on site
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")    
    error = None
    cursor = get_db().cursor()
    username = request.form['username']
    password =  request.form["password"]
    sql_query = 'SELECT ID, PASSWORD FROM login WHERE username = ?'
    cursor.execute(sql_query, (username,))
    results = cursor.fetchall()
    if bool(results):
        if check_password_hash(results[0][1], password):
            session["logged_in"] = True
            user_id = results[0][0]
            return redirect('/')
    if username == '' and password == '':
        return redirect('/')
    if username == '' or password == '' or username.isspace():
        error = "Please enter a valid username and password."
    else:
        error = "Please enter a valid username and password."
    return render_template("login.html", error=error)

# log out of site
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect("/")
    flash("You were just logged out")

# users can view products and read about what they are
@app.route('/menu')
def menu():
    return render_template("menu.html")

# ordering system using database and foreign keys
@app.route("/drink_order", methods=["GET", "POST"])
def order():
    if 'logged_in' not in session:
        return redirect("/login")
    extras = "SELECT id, name FROM additives"
    cursor = get_db().cursor()
    cursor.execute(extras)
    additives = cursor.fetchall()

    degrees = "SELECT id, temperature FROM temperature"
    cursor = get_db().cursor()
    cursor.execute(degrees)
    temperature = cursor.fetchall()

    drinks = "SELECT id, name FROM flavour;"
    cursor = get_db().cursor()
    cursor.execute(drinks)
    flavour = cursor.fetchall()

    customer_id = "SELECT id, username FROM login;"
    cursor = get_db().cursor()
    cursor.execute(customer_id)
    name = cursor.fetchall()

    items = "SELECT username, name, temperature, additives FROM drink_order;"
    cursor = get_db().cursor()
    cursor.execute(items)
    goods = cursor.fetchall()

    return render_template('drink_order.html', temperature=temperature, additives=additives,  flavour=flavour, goods=goods, name=name, admin = admin, user_id=user_id)

# add order to drink order
@app.route("/add", methods={"GET", "POST"})
def add():
    if request.method == "POST":
        cursor = get_db().cursor()
        user_id = username
        drink_name = request.form['drink_name']
        drink_temperature = request.form["drink_temperature"]
        drink_additives = request.form["drink_additives"]
        sql = "INSERT INTO drink_order(username, name, temperature, additives) VALUES (?,?,?,?)"
        cursor.execute(sql,(user_id, drink_name, drink_temperature, drink_additives))
        get_db().commit()
    return redirect("/drink_order")

# users logged in can delete their orders 
@app.route('/delete' , methods=["GET", "POST"])
def delete():
    if 'logged_in' not in session:
        return redirect("/drink_order")
    if request.method == 'POST':
        cursor = get_db().cursor()
        customer_username = int(request.form["customer_name"])
        sql = "DELETE FROM drink_order WHERE id=?"
        cursor.execute(sql,(customer_username,))
        get_db().commit()
    return redirect('/drink_order')


# inform if site has a problem
if __name__ == "__main__":
    app.run(debug=True)




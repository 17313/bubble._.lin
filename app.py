from flask import Flask, render_template, g, request, redirect, session, flash, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DATABASE = 'Bubble._.Lin.db'
global admin
admin = False

app.secret_key = 'bubbles'

# get database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# closes connection to database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    return

# create an app route
@app.route('/')
def index():
    # link to index html template
    return render_template('index.html')

'''def check_user(username, password):
    # get the user from the database
    user = 'user'
    if user and check_password_hash(user[1], password):
        session['user'] = user[0] # store the user id in session
        return True
    return False

def create_user(username, password):
    password_hashed = generate_password_hash(password)
    # add to database
    sql = "INSERT INTO login(password) VALUES ?"
    cursor.execute(sql,(password))

def get_user():
    user_id = session['user']
    if user_id:
        # get from the database the user by id
        pass
    return False

def logout_user():
    session.pop('user')'''

# sign up and insert information into database
@app.route('/signup', methods=["GET", "POST"])
def signup():
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
    cursor.execute(sql_query, (new_username, generate_password_hash(new_password, )))
    get_db().commit()
    sql_query = "SELECT ID FROM login WHERE username = ?"
    cursor.execute(sql_query, (new_username,))
    global user_id
    user_id = cursor.fetchall()[0][0]
    session["logged_in"] = True
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
            global user_id
            user_id = results[0][0]
            return redirect('/')
    if username == '' and password == '':
        return redirect('/')
    if username == '' or password == '' or username.isspace():
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

    items = "SELECT username, name, temperature, additives FROM drink_order;"
    cursor = get_db().cursor()
    cursor.execute(items)
    goods = cursor.fetchall()

    return render_template('drink_order.html', temperature=temperature, additives=additives,  flavour=flavour, goods=goods, admin = admin)

# add order to drink order
@app.route("/add", methods={"GET", "POST"})
def add():
    if request.method == "POST":
        cursor = get_db().cursor()
        customer_name = request.form['customer_name']
        drink_name = request.form['drink_name']
        drink_temperature = request.form["drink_temperature"]
        drink_additives = request.form["drink_additives"]
        sql = "INSERT INTO drink_order(username, name, temperature, additives) VALUES (?,?,?,?)"
        cursor.execute(sql,(customer_name, drink_name, drink_temperature, drink_additives))
        get_db().commit()
    return redirect("/drink_order")

# users logged in can delete their orders 
@app.route('/delete' , methods=["GET", "POST"])
def delete():
    if 'logged_in' not in session:
        return redirect("/drink_order")
    if request.method == 'POST':
        cursor = get_db().cursor()
        customer_username = str(request.form["customer_name"])
        sql = "DELETE FROM drink_order WHERE id=?"
        cursor.execute(sql,(customer_username,))
        get_db().commit()
    return redirect('/drink_order')


# inform if site has a problem
if __name__ == "__main__":
    app.run(debug=True)




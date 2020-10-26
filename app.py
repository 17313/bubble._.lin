#grabbing imports from flask
import sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

#-------------------------------------------------------------------------------------------------------#

app = Flask(__name__)
DATABASE = 'Bubble._.Lin.db'
global admin
admin = False

#-------------------------------------------------------------------------------------------------------#

#create a secret key to ensure safety of user information
app.secret_key = 'bubbles'

#-------------------------------------------------------------------------------------------------------#

def get_db():
    '''get database using link from above variable called DATABASE to be used for storing data'''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#-------------------------------------------------------------------------------------------------------#

@app.teardown_appcontext
def close_connection(exception):
    '''ensure that the proccess doesnt crash if database connection has an issue by disconnecting'''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close() 
    return

#-------------------------------------------------------------------------------------------------------#

def get_user():
    if session.get("user"):
        '''grab user id from database to be used in the functions'''
        user = "SELECT username FROM drink_order WHERE id =?" #sql statement to grab user id from database to be used in the functions
        cursor = get_db().cursor()
        cursor.execute(user)
        username = cursor.fetch(1)
        pass
    return False

#-------------------------------------------------------------------------------------------------------#

@app.route('/')
def index():
    '''make an app route and link to index html template'''
    cursor =  get_db().cursor()
    sql = "SELECT name, images FROM flavour" #sql statement to show images from the datbase which will be be sent to the html for a function the code more efficient
    cursor.execute(sql)
    results = cursor.fetchall()

    return render_template('index.html', results=results)

#-------------------------------------------------------------------------------------------------------#

@app.route('/signup', methods=["GET", "POST"])
def signup():
    '''sign up and insert information into database'''
    if request.method == "GET" :
        return render_template("signup.html")
    error=None
    cursor = get_db().cursor()
    new_username = request.form["username"] #variable to be used in an SQL statement to input new users username into the databasev
    new_password = request.form["password"] #variable to be used in an SQL statement to input new users password into the database
    if new_username == "" or new_password == "":
        error = "Please enter a username and a password" #ensure the input is within reason using an if statement and if it doesnt comply then print error and to retry
        return render_template("signup.html", error=error)
    sql_query = "SELECT username FROM login WHERE username = ?"
    cursor.execute(sql_query, (new_username,))
    if bool(cursor.fetchall()):
        error = "Username already taken. Please try again" #if username is already found in database, ensure there cannot be repeats by asking for them to try another one
        return render_template("signup.html", error=error)
    sql_query = "INSERT INTO login (username, password) VALUES (?,?)" #SQL statement with a tuple to insert new users username and password into database for  future use
    '''insert new username and password into database'''
    cursor.execute(sql_query, (new_username, generate_password_hash(new_password, )))
    get_db().commit()
    return redirect("/")
    
#-------------------------------------------------------------------------------------------------------#

@app.route('/login', methods=["GET", "POST"])
def login():
    '''using the user input and matching and searching the database to see if an existing username and password exists and then giving them access to ordering function'''
    if request.method == "GET":
        return render_template("login.html")    
    error = None
    cursor = get_db().cursor()
    username = request.form['username'] #variable to help search through user database to see if the inputted username matches one in the database
    password =  request.form["password"] #variable to help search through user database to see if the inputted password matches one in the database
    sql_query = 'SELECT ID, PASSWORD FROM login WHERE username = ?'
    cursor.execute(sql_query, (username,))
    results = cursor.fetchall()
    if bool(results):
        if check_password_hash(results[0][1], password): #use an if statement to see if the variables inputted and the dat
            session["logged_in"] = True
            user_id = results[0][0]
            session["user_id"] = user_id #using session import with variable to make it usable in othewr function
            return redirect('/')
    if username == '' and password == '':
        return redirect('/')
    if username == '' or password == '' or username.isspace(): #make logging in function bullet proof with if statements 
        error = "Please enter a valid username and password."
    else:
        error = "Please enter a valid username and password."
    return render_template("login.html", error=error)

#-------------------------------------------------------------------------------------------------------#

@app.route('/logout')
def logout():
    '''function for logging out of site'''
    session.pop('logged_in', None)
    return redirect("/")
    flash("You were just logged out")

#-------------------------------------------------------------------------------------------------------#

@app.route('/menu')
def menu():
    '''users can view products from the database and read about what they are and the price'''
    drink = "SELECT name, price, description, images FROM flavour"
    cursor =  get_db().cursor()
    cursor.execute(drink)
    flavour = cursor.fetchall()
    return render_template("menu.html", flavour=flavour)

#-------------------------------------------------------------------------------------------------------#

# ordering system using database and foreign keys
@app.route("/drink_order", methods=["GET", "POST"])
def order():
    '''data from database to be used in the html returned as variables to be used in order function'''
    if 'logged_in' not in session:
        return redirect("/login")
    extras = "SELECT id, name, price FROM additives" #additive id, name and price grabbed from table additives in the database to be used in order function
    cursor = get_db().cursor()
    cursor.execute(extras)
    additives = cursor.fetchall()

    degrees = "SELECT id, temperature FROM temperature" #temperature id and temperature grabbed from table temperature in the database to be used in order function
    cursor = get_db().cursor()
    cursor.execute(degrees)
    temperature = cursor.fetchall()

    drinks = "SELECT id, name, price FROM flavour;" #drink id, name and price grabbed from table flavour in the database to be used in order function
    cursor = get_db().cursor()
    cursor.execute(drinks)
    flavour = cursor.fetchall() 

    items = "SELECT id, username, name, temperature, additives, price FROM drink_order" #drink order id, username, name, temperature, additives and price grabbed from table drink order in the database to be used in order function
    cursor = get_db().cursor()
    cursor.execute(items)
    goods = cursor.fetchall()

    sql = "SELECT username FROM login WHERE id= ?" #customer id and name grabbed from table additives in the database to be used in order function
    cursor.execute(sql,(session["user_id"],))
    customer_name = cursor.fetchone()[0]
    return render_template('drink_order.html', temperature=temperature, goods=goods, flavour=flavour, additives=additives, customer_name=customer_name)

#-------------------------------------------------------------------------------------------------------#

# a function that adds 
@app.route("/add", methods={"GET", "POST"})
def add():
    '''add function to take inputs and insert them into the database'''
    if request.method == "POST":
        cursor = get_db().cursor()
        sql = "SELECT username FROM login WHERE id= ?" #customer id and name grabbed from table additives in the database to be used in order function
        cursor.execute(sql,(session["user_id"],))
        customer_name = cursor.fetchone()[0]
        drink_name = request.form['drink_name']
        sql = 'SELECT price FROM flavour WHERE name = ?' #grab drink price from table flavour to be used to find total price to show in website
        cursor.execute(sql,(drink_name,))
        drink_price = cursor.fetchone()[0]
        drink_temperature = request.form["drink_temperature"]
        drink_additives = request.form["drink_additives"]
        sql = 'SELECT price FROM additives WHERE name = ?' #grab additive price from table additive to be used to find total price to show in website
        cursor.execute(sql,(drink_additives,))
        additive_price = cursor.fetchone()[0]
        price = drink_price + additive_price
        sql = "INSERT INTO drink_order(username, name, temperature, additives, price) VALUES (?,?,?,?,?)" #sql statement to insert all drink inputs into the database in table drink order
        cursor.execute(sql,(customer_name, drink_name, drink_temperature, drink_additives, price))
        get_db().commit()
    return redirect("/drink_order")

#-------------------------------------------------------------------------------------------------------#

@app.route('/delete' , methods=["GET", "POST"])
def delete():
    '''users logged in can delete their orders'''
    if request.method == 'POST':
        cursor = get_db().cursor()
        order_id = request.form["order_id"]
        sql = "DELETE FROM drink_order WHERE id=?" #sql statement to delete orders from database
        cursor.execute(sql,(order_id,))
        get_db().commit()
    return redirect('/drink_order')

#-------------------------------------------------------------------------------------------------------#

# inform if site has a problem
if __name__ == "__main__":
    app.run(debug=True)

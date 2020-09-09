
from flask import Flask, render_template, g , request, redirect, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DATABASE = 'Bubble._.Lin.db'
global admin
admin = False
global user_id
user_id = None




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

def sum():
    total = "SELECT SUM(price)"

@app.route('/')
def index():
    '''make an app route and link to index html template'''
    cursor =  get_db().cursor()
    sql = "SELECT images, name FROM image"
    cursor.execute(sql)
    results = cursor.fetchall()

    return render_template('index.html', results=results)




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
            print(user_id)
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
    cursor =  get_db().cursor()
    sql = "SELECT images FROM image"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor =  get_db().cursor()
    sql = "SELECT name, price, description FROM flavour"
    cursor.execute(sql)
    description = cursor.fetchall()
    print(results)
    return render_template("menu.html", results=results, length=range(len(results)), description=description)

# ordering system using database and foreign keys
@app.route("/drink_order", methods=["GET", "POST"])
def order():
    if 'logged_in' not in session:
        return redirect("/login")
    extras = "SELECT id, name, price FROM additives"
    cursor = get_db().cursor()
    cursor.execute(extras)
    additives = cursor.fetchall()

    degrees = "SELECT id, temperature FROM temperature"
    cursor = get_db().cursor()
    cursor.execute(degrees)
    temperature = cursor.fetchall()

    drinks = "SELECT id, name, price FROM flavour;"
    cursor = get_db().cursor()
    cursor.execute(drinks)
    flavour = cursor.fetchall() 

    items = "SELECT username, name, temperature, additives, price FROM drink_order"
    cursor = get_db().cursor()
    cursor.execute(items)
    goods = cursor.fetchall()

#-------------------------------------------------------------------------------#

    flavour_price = "SELECT price FROM flavour"
    cursor = get_db().cursor()
    cursor.execute(flavour_price)
    drink_price = cursor.fetchone() 

    extras_price = "SELECT price FROM additives"
    cursor = get_db().cursor()
    cursor.execute(extras_price)
    additives_price = cursor.fetchone() 



    return render_template('drink_order.html', temperature=temperature, additives=additives,  flavour=flavour, goods=goods, additive_price=additive_price,drink_price=drink_price)

# add order to drink order
@app.route("/add", methods={"GET", "POST"})
def add():
    if request.method == "POST":
        cursor = get_db().cursor()
        drink_name = request.form['drink_name']
        drink_temperature = request.form["drink_temperature"]
        drink_additives = request.form["drink_additives"]
        price = request.form['additive_price'] + request.form['drink_price']
        sql = "INSERT INTO drink_order(username, name, temperature, additives, price) VALUES (?,?,?,?,?)"
        cursor.execute(sql,(user_id, drink_name, drink_temperature, drink_additives, price,))
        get_db().commit()
    return redirect("/drink_order")

# users logged in can delete their orders 
@app.route('/delete' , methods=["GET", "POST"])
def delete():

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




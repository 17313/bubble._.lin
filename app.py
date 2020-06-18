from flask import Flask, render_template, g, request, redirect, session

import sqlite3

app = Flask(__name__)
DATABASE = 'Bubble._.Lin.db'

app.secret_key = 'bubbles'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'username' or request.form['password'] != 'password':
            error = "Invalid credentials. Please try again"
        else:
            session['logged_in'] = True
            flash("Ypu were just logged in")
            return redirect("/")
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You were just logged out")
    return redirect("/")

@app.route('/menu')
def menu():
    return render_template("menu.html")

@app.route("/drink_order")
def order():   
    sql = "SELECT * FROM 'drink_order';"
    cursor = get_db().cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('drink_order.html' , results=results)

@app.route("/add", methods={"GET", "POST"})
def add():
    if request.method == "POST":
        cursor = get_db().cursor()
        customer_name = request.form['username']
        drink_name = request.form['drink_name']
        drink_temperature = request.form["drink_temperature"]
        drink_additives = request.form["drink_additives"]
        sql = "INSERT INTO 'drink_order'(username, name, temperature, additives) VALUES (?,?,?,?)"
        cursor.execute(sql,(customer_name, drink_name, drink_temperature, drink_additives))
        get_db().commit()
    return redirect("/drink_order")

@app.route('/delete' , methods=["GET", "POST"])
def delete():
    error = None
    if request.method == 'POST':
        if request.form['password'] != 'order':
            error = "Invalid credentials. Please try again"
        else:
            cursor = get_db().cursor()
            id = int(request.form["username"])
            sql = "DELETE FROM 'drink_order' WHERE id=?"
            cursor.execute(sql,(id,))
            get_db().commit()
    return redirect('/drink_order')



if __name__ == "__main__":
    app.run(debug=True)




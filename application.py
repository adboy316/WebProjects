import os
import requests
import json

from flask import Flask, session, render_template, request, flash, redirect, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import BooksSearch

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return search()

@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form.get("username")
    password = request.form.get("psw")
    user = db.execute("SELECT * FROM users WHERE username = :username",
                      {"username": username}).fetchone()
    if user is None:
        flash('wrong username or password!')
        return index()
    else:
        session['username'] = username
        session['logged_in'] = True
    return search()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = request.form
    if request.method == 'POST':
        username = request.form.get("username")
        check_username = db.execute("SELECT username FROM users WHERE username = :username",
                      {"username": username})
        if check_username.fetchone() is not None:
            flash("That username is already taken...")
            return render_template('register.html')
            

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("psw")
        favbook = request.form.get("favbook")

        db.execute("INSERT INTO users (firstname, lastname, username, password, favbook) VALUES (:firstname, :lastname, :username, :password, :favbook)",
                   {"firstname": firstname, "lastname": lastname, "username": username, "password": password, "favbook": favbook})
        db.commit()
    return render_template('register.html', form=form)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()


@app.route("/search")
def search():
    return render_template('search.html')


@app.route("/api/<string:isbn>", methods=['GET'])
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                      {"isbn": isbn}).fetchone()
    if book is None:
        abort(404)
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"yK55H7YAkLXrGzmsikTkw": "KEY", "isbns": isbn})
    res = res.json()
    data = json.dumps({'title': book.title, 'author': book.author, 'year': book.year, 'isbn': book.isbn,
                       'review_count': res['books'][0]['work_text_reviews_count'], 'average_score': res['books'][0]["average_rating"]})

    return render_template("api.html", book=book, data=data)


@app.route("/books/<string:isbn>", methods=['GET', 'POST'])
def bookpage(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                      {"isbn": isbn}).fetchone()
    if book is None:
        abort(404)

    user = session['username']
    reviewed = db.execute("SELECT title FROM reviews JOIN users ON reviews.username = :user JOIN books ON reviews.isbn = :isbn", {
                          "isbn": isbn, "user": user}).fetchall()
    bookreviews = db.execute(
        "SELECT * FROM reviews WHERE isbn =:isbn", {"isbn": isbn})

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"yK55H7YAkLXrGzmsikTkw": "KEY", "isbns": isbn})

    if request.method == 'POST':
        form = request.form
        review = request.form.get("review")
        rating = request.form.get("rating")
        reviewtitle = request.form.get("reviewtitle")
        isbn = str(isbn)
        db.execute("INSERT INTO reviews (review, reviewtitle, rating, isbn, username) VALUES (:review, :reviewtitle, :rating, :isbn, :user)",
                   {"review": review, "rating": rating, "user": user, "isbn": isbn, "reviewtitle": reviewtitle})
        db.commit()
        return redirect(url_for('bookpage', isbn=isbn))

    return render_template("books.html", book=book, reviewed=reviewed, user=user, bookreviews=bookreviews, res=res.json())


@app.route('/results', methods=["POST"])
def search_results():
    results = []
    search_string = str(request.form.get("query"))
    # Get all books.
    search_results = db.execute(
        "SELECT * FROM books  WHERE title || isbn || author ~* :search_string LIMIT 10", {"search_string": search_string})

    return render_template("results.html", search_results=search_results)

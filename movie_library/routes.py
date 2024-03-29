
# --------------------------- Imports --------------------------- #

# Imports
import uuid # To create unique id numbers
import datetime # To get the current date and time
import functools # Necessary for wrappers

from flask import (
    current_app, 
    Blueprint, 
    render_template, 
    session, 
    redirect, 
    request, 
    url_for,
    flash )

# Import for hashing
from passlib.hash import pbkdf2_sha256

# Import asdict
from dataclasses import asdict

# Import the classes from other pythonfiles
from movie_library.models import Movie, User
from movie_library.forms import (
    MovieForm, 
    ExtendedMovieForm, 
    RegisterForm, 
    LoginForm )


# --------------------- Create Blueprint ------------------------ #

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static")


# -------------------- Create Decorator (for login) ---------------- #

# Any endpoints that uses this decorator, will be replaced by the function route_wrapper()
# This decorator can now be used for each endpoint for which a user has to be logged in !

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        
        return route(*args, **kwargs)
    
    return route_wrapper


# --------------------- Endpoints / Routes --------------------------- #

# Endpoint for index
@pages.route("/") # Note that we start here with pages, to indicate that this route is part of the blueprint we created above.
@login_required # Here we decorate this endpoint
def index():

    # Error if the user within the session is not present in the database!
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data) # ** means unpacked keyword argument

    movie_data = current_app.db.movie.find({"_id": {"$in": user.movies}})

    # movies is an list of classobjects
    movies = [ Movie(**movie) for movie in movie_data] 
    # ** means unpacked keyword argument

    return render_template(
        "index.html",
        title="Movies Watchlist",
        movies_data=movies
    )

# Endpoint for register
@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )

        current_app.db.user.insert_one(asdict(user))

        # Flash message
        flash("User registered succesfully", "succes")

        return redirect(url_for(".login"))

    return render_template("register.html", title="Movies Watchlist - Register", form=form)

# Endpoint for login
@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect( url_for(".index") )

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        # form.email.data this one isn't empty if there is a form posted
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)
        # This is going to create a keyword argument for each value in the dict from find_one

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email 

            return redirect(url_for(".index"))
        
        flash("Login credentials not correct", category="danger")
    
    return render_template("login.html", title="Movie Watchlist - Login", form=form)

# Endpoint for logout
@pages.route("/logout")
def logout():
    current_theme = session.get("theme")
    session.clear() # This will also change the light/dark theme
    session["theme"] = current_theme    

    return redirect(url_for(".login"))

# Endpoint for adding a movie
@pages.route("/add", methods=["GET", "POST"])
@login_required # Here we decorate this endpoint
def add_movie():
    # Here we create an object of the class:
    form = MovieForm()

    # if request.method == "POST":
    # The next if statements puts error-message into the form object if the validation is false!
    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data
        )
 
        # Now we add this movie to our database, for this you need to setup your MongoDBdatabase!:
        # asdict create dictonary from class-object
        current_app.db.movie.insert_one(asdict(movie))

        current_app.db.user.update_one(
            {"_id": session["user_id"] }, {"$push": {"movies": movie._id} }
        )
  
        return redirect( url_for(".index") )


    return render_template(
        "new_movie.html",
        title="Movies watchlist - Add Movie",
        form=form
        # Here we pass the object to the template
    )

# Endpoint for editing a movie
@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required # Here we decorate this endpoint
def edit_movie(_id:str): # It takes in id number which has to be a string
    movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    form = ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data

        movie.title = form.title.data
        movie.description = form.description.data
        movie.year = form.year.data    

        current_app.db.movie.update_one({"_id": movie._id}, {"$set": asdict(movie)} )
        return redirect(url_for(".movie", _id=movie._id) )

    return render_template("movie_form.html", movie=movie, form=form)

# Endpoint for movie-data
# Never use just 'id' as a variable, because that is already a function in Python
@pages.get("/movie/<string:_id>")
def movie(_id: str):
    # get the movie from the database
    # and create movie class-object:
    movie = Movie(**current_app.db.movie.find_one({"_id": _id}))

    return render_template("movie_details.html", movie=movie)

# Endpoint for movie-rating
@pages.get("/movie/<string:_id>/rate")
@login_required # Here we decorate this endpoint
def rate_movie(_id):
    # He chose to get the rating from the query string parameter, i.e.d.
    # "/movie/<string:_id>/rate?rating=4"
    rating = int(request.args.get("rating"))
    # here we change the rating in the database!:
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"rating":rating}} )

    return redirect(url_for(".movie", _id=_id) )

# Endpoint for movie-last-watched
@pages.get("/movie/<string:_id>/watch")
@login_required # Here we decorate this endpoint
def watch_today(_id):
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"last_watched": datetime.datetime.today() }} )
    return redirect( url_for(".movie", _id=_id) )

# Endpoint for adjust theme
@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark" 
    
    return redirect( request.args.get("current_page" ) )
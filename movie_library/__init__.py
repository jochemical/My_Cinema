# This __init__.py file will run when starting Flask and automatically the create_app() function is called

# -------------------- Imports ----------------------- #

import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

# Import our pages from routes
from movie_library.routes import pages


# ------------------------- Create app ---------------------------- #

# Load environment variables
load_dotenv()

# The create_app() function is automatically called when runnning flask
def create_app():

    # First we create the Flask app
    app = Flask(__name__)

    # Here we get the correct MONGODB_URI (you have to add this by yourself)
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")

    # A secret key is used for the cookies, so also the session
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Here we create the database for our app
    app.db = MongoClient(app.config["MONGODB_URI"]).movies #.get_default_database()

    # To create this app, we will get our routes (or endpoints) from routes.py, by using blueprints
    # Therefore, we import pages from routes.py at the top, and we register these blueprints in the line below
    app.register_blueprint(pages)

    # Return the app for Flask
    return app
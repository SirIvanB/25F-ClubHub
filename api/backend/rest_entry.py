from flask import Flask
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

from backend.db_connection import db
from backend.simple.simple_routes import simple_routes
from backend.events.event_routes import events
from backend.clubs.club_routes import club_routes
from backend.students.student_routes import student_routes
from backend.admin.admin_routes import admin_routes
from backend.analytics.analytics_routes import analytics_routes
from backend.invitations.invitations_routes import invitation_routes

def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Configure file logging if needed
    #   Uncomment the code in the setup_logging function
    # setup_logging(app) 

    # Load environment variables
    # This function reads all the values from inside
    # the .env file (in the parent folder) so they
    # are available in this file.  See the MySQL setup
    # commands below to see how they're being used.
    load_dotenv()

    # secret key that will be used for securely signing the session
    # cookie and can be used for any other security related needs by
    # extensions or your application
    # app.config['SECRET_KEY'] = 'someCrazyS3cR3T!Key.!'
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # # these are for the DB object to be able to connect to MySQL.
    # app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv(
        "DB_NAME"
    ).strip()  # Change this to your DB name

    # Initialize the database object with the settings above.
    app.logger.info("current_app(): starting the database connection")
    db.init_app(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each
    app.logger.info("create_app(): registering blueprints with Flask app object.")
    app.register_blueprint(simple_routes)
    app.register_blueprint(events)
    app.register_blueprint(club_routes, url_prefix="/clubs")
    app.register_blueprint(student_routes, url_prefix="/students")
    app.register_blueprint(admin_routes, url_prefix="/admin")
    app.register_blueprint(analytics_routes, url_prefix="/analytics")
    app.register_blueprint(invitation_routes, url_prefix="/invitations")

    # Don't forget to return the app object
    return app

def setup_logging(app):
    """
    Configure logging for the Flask application in both files and console (Docker Desktop for this project)
    
    Args:
        app: Flask application instance to configure logging for
    """
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')

    ## Set up FILE HANDLER for all levels
    # file_handler = RotatingFileHandler(
    #     'logs/api.log',
    #     maxBytes=10240,
    #     backupCount=10
    # )
    # file_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    # ))
    
    # Make sure we are capturing all levels of logging into the log files. 
    # file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    # app.logger.addHandler(file_handler)

    # ## Set up CONSOLE HANDLER for all levels
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s'
    # ))
    # Debug level capture makes sure that all log levels are captured
    # console_handler.setLevel(logging.DEBUG)
    # app.logger.addHandler(console_handler)
    pass
    
    
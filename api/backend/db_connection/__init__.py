#------------------------------------------------------------
# This file creates a shared DB connection resource
#------------------------------------------------------------
from flaskext.mysql import MySQL
from pymysql import cursors


# the parameter instructs the connection to return data 
# as a dictionary object. 
db = MySQL(cursorclass=cursors.DictCursor)

# Custom cursor method to make db.cursor() work with Flask-MySQL
def cursor(dictionary=True):
    return db.get_db().cursor()

# Custom commit method
def commit():
    return db.get_db().commit()

# Attach methods to db object
db.cursor = cursor
db.commit = commit
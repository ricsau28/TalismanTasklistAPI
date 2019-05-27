# talismansoftwaresolutions/users/views.py

from functools import wraps
from flask import Blueprint, session, request, jsonify, \
    redirect, url_for
from talismansoftwaresolutions.models import User
from talismansoftwaresolutions import db

users_blueprint = Blueprint('users', __name__)

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('users.login'))
    return wrap


@users_blueprint.route('/api/v1/users/login', methods = ['POST'])
def login():
    data = request.get_json(force = True)
    pwd = data.get('password') 
    message = "Hello, {}". format(data.get('username'))
    greeting = {"greeting": message}
    #return "Hello, {}". format(data.get('username'))
    return jsonify(greeting)   

@users_blueprint.route('/api/v1/users/get_user_id', methods = ['POST'])
def get_user_id():
    #name, email, password
    data = request.get_json(force = True)
    name = data.get('user_name', None)
    pwd = data.get('password', None) 
    email = data.get('email', None)

    user = User(name, email, pwd)

    msg = None

    try:
        user_id = db.getUserID(user)
        msg = "{}".format(user_id)        
    except Exception as e:
        user_id = -32
        msg = "{} {}".format(user_id, e)

    status = {"Status": msg}

    return jsonify(status)


@users_blueprint.route('/api/v1/users/add_user', methods = ['POST'])
def add_user():
    #name, email, password
    db_exception = None

    data = request.get_json(force = True)
    name = data.get('user_name', None)
    pwd = data.get('password', None)     
    email = data.get('email', None)

    user = User(name, email, pwd)       
    user_id, db_exception = db.addNewUser(user)

    if(db_exception is None):    
        msg = "{}".format("User added")
    else:
        msg = "Error code: {}, Details: {}".format(db_exception.pgcode, db_exception)

    #listElements = [{"user_id": user_id}, {"status": msg}]
    status = {"Status": [{"user_id": user_id}, {"status": msg}]}

    return jsonify(status)

"""
@users_blueprint.route('/api/v1/users/add_user', methods = ['POST'])
def add_user():
    #name, email, password
    data = request.get_json(force = True)
    name = data.get('user_name', None)
    pwd = data.get('password', None) 
    email = data.get('email', None)    

    db_exception = None   

    user = User(name, email, pwd)   

    try:
        user_id, db_exception = db.addNewUser(user)
        if(db_exception is None):    
            msg = "{}".format("User added")
        else:
            msg = "({}) Error code, Details: {}".format(e.pgcode, db_exception)
            
        
        #if(user_id == -17):
        #    msg = "{} already exists in the database".format(name)
        #else:    
        #    msg = "{}".format("User added")
        
    except Exception as e:
        user_id = -33
        msg = "{} {()} {}".format(user_id, error_code, e)

    listElements = [{"user_id": user_id}, {"status": msg}]

    status = {"Status": listElements}

    return jsonify(status)
    """
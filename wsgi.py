#!/usr/bin/python3


import os
os.chdir(os.path.dirname(__file__))
import logging
from bottle import app, hook, run, post, request, response, get, route, template, HTTPResponse
import bottle
from beaker.middleware import SessionMiddleware
import json
import configparser
import pathlib
import mysql.connector
from pprint import pformat

# To disable for production
#import cgitb
#cgitb.enable()

data_dir = '/home/data/FertilityCare'
users_data_dir = data_dir + '/users_data'
user_data_file_name = 'user_data.json'
application_dir = '/home/jbh/Development/cycle'
www_user_dir = '/home/www/jb_dedi_web'
www_user_log_dir = www_user_dir + '/logs'
www_user_log_file = www_user_log_dir + '/python.log'

# Log level:
# DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.basicConfig(filename=www_user_log_file,level=logging.DEBUG)

session_opts = {
    'session.type': 'file',
    # session.cookie_expires in seconds
    'session.cookie_expires': 300,
    'session.data_dir': data_dir + '/sessions',
    'session.auto': True
}

application = SessionMiddleware(bottle.app(), session_opts)

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

@route('/')
def hello():
    return "REST API for FertilityCare data"

@route('/', method='OPTIONS')
def trigger_method_options():
    return 0

@route('/', method='POST')
def process():
    response = do_action(request.json)
    return response

def return_bottle(status, data=""):
    return bottle.HTTPResponse(status=status, body=data)

def return_status(status=0, data=""):
    data_to_return = { 'status': status, 'data': data }
    logging.debug("Return status: ")
    logging.debug(pformat(data_to_return))
    return data_to_return

def get_user_query(table_name='users'):
    return ("SELECT id FROM " + table_name + " WHERE email=%s AND password=PASSWORD(%s) AND enabled=1")

def check_user_in_database(email, password):
    user_id = 0
    config = configparser.ConfigParser();
    config.read(application_dir + '/config.ini')
    db_config = {
        'user': config['DB']['db_user'],
        'password': config['DB']['db_password'],
        'host': config['DB']['db_host'],
        'database': config['DB']['db_name'],
        'port': config['DB']['db_port']
    }
    
    try:
        cnx = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return return_status(1, "Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return return_status(1, "Database does not exist")
        else:
            return return_status(1, err)
    else:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(get_user_query(), (email, password))
        for (data) in cursor:
            user_id = data['id']
        cursor.close()
        cnx.close()
    if user_id == 0:
        return return_status(1, "Invalid credentials")
    else:
        return return_status(0, user_id)

def do_action(data):
    action = data['action']
    logging.debug("ACTION: " + action)
    if action == 'login':
        return login(data['credentials'])
    elif action == 'logout':
        return logout()
    elif action == 'GetData':
        return get_data()
    elif action == 'SetData':
        return set_data(data['data'])
    else:
        return unknown_action()

def check_user_logged_in():
    return 'user_id' in request.session

def login(credentials):
    if not check_user_logged_in():
        logging.debug("New login")
        login_status = check_user_in_database(credentials['email'], credentials['password'])
        if login_status['status'] != 0:
            logging.debug("Login failed: " + login_status['data'])
            return return_bottle(500, login_status['data'])

        request.session['user_id'] = login_status['data']
    else:
        logging.debug("Login: already logged in")

    logging.debug("User id: " + str(request.session['user_id']))
    return return_status()

def reset_session():
    request.session.delete()

def logout():
    if not check_user_logged_in():
        logging.debug("Logout: already logged out")
        return return_status()
    else:
        reset_session()
        return return_status()

def get_user_data_dir():
    return users_data_dir + '/' + str(request.session['user_id'])

def get_user_data_file():
    return get_user_data_dir() + '/' + user_data_file_name

def get_data():
    if not check_user_logged_in():
        return return_bottle(403, 'User not logged in')
    else:
        user_data_dir = get_user_data_dir()
        user_data_file = get_user_data_file()
        if not os.path.isdir(user_data_dir):
            return return_status(0, {})
        if not os.path.exists(user_data_file):
            return return_status(0, {})
        with open(user_data_file) as json_file:
            return return_status(0, json.load(json_file))
        return return_status(0, {})

def set_data(data):
    if not check_user_logged_in():
        return return_bottle(403, 'User not logged in')
    else:
        user_data_dir = get_user_data_dir()
        user_data_file = get_user_data_file()
        if not os.path.isdir(user_data_dir):
            pathlib.Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        with open(user_data_file, 'w+') as json_file:
            json.dump(data, json_file)
        return return_status()

def unknown_action():
    return return_bottle(500, 'Unknown action')

#run(host='localhost', port=1234, debug=True, app=application)


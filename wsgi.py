#!/usr/bin/python3


import os
os.chdir(os.path.dirname(__file__))
from bottle import app, hook, run, post, request, response, get, route, template, HTTPResponse
import bottle
from beaker.middleware import SessionMiddleware
import json
from pprint import pprint
import configparser
import mysql.connector

# To disable for production
#import cgitb
#cgitb.enable()

data_dir = '/home/data/FertilityCare/'
application_dir = '/home/jbh/Development/cycle'

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': data_dir + '/sessions',
    'session.auto': True
}

#application = bottle.app()
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
    pprint(request.json)
    response = do_action(request.json)
    
    #data = {'2019216': {'comment': '',
    #                  'creationDate': 1552735477141,
    #                  'frequency': 1,
    #                  'misc': {},
    #                  'modificationDate': 1553636161261,
    #                  'mucus': 1,
    #                  'mucusExtended': {},
    #                  'period': -1,
    #                  'sticker': '0'}}
    return response

def return_status(status, data=""):
    return { 'status': status, 'data': data }

def get_user_query(table_name='users'):
    return ("SELECT id FROM " + table_name + " WHERE email=%s AND password=PASSWORD(%s) AND enabled=1")

def login_user(email, password):
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
    print("ACTION: " + action)
    function = {
       'login' : login,
       'GetData': get_data,
       'SetData': set_data
    }.get(data['action'], unknown_action)
    return function(data)

def check_user_logged_in():
    return 'user_id' in request.session

def login(data):
    credentials = data['credentials']
    if not check_user_logged_in():
        print("New login")
        login_status = login_user(credentials['email'], credentials['password'])
        if login_status['status'] != 0:
            print("Login failed: " + login_status['data'])
            return bottle.HTTPResponse(status=500, body=login_status['data'])

        request.session['user_id'] = login_status['data']
    else:
        print("Already logged in")

    print("User id: " + str(request.session['user_id']))
    return {}


def get_data(data):
    if not check_user_logged_in():
        return bottle.HTTPResponse(status=403, body='User not logged in')
    else:
        return {}

def set_data(data):
    if not check_user_logged_in():
        return bottle.HTTPResponse(status=403, body='User not logged in')
    else:
        return {}

def unknown_action():
    return bottle.HTTPResponse(status=500, body='Unknown action')

run(host='localhost', port=1234, debug=True, app=application)


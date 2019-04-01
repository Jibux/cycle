#!/usr/bin/python3


import os
os.chdir(os.path.dirname(__file__))
from bottle import app, run, post, request, response, get, route, template, HTTPResponse
import bottle
import json
from pprint import pprint
import configparser
import mysql.connector

# To disable for production
#import cgitb
#cgitb.enable()

application = bottle.app()

data_dir = '/home/data/FertilityCare/'
application_dir = '/home/jbh/Development/cycle'

get_user_query = ("SELECT id FROM %s WHERE email='%s' AND password=PASSWORD(%s) AND enabled=1")

@application.route('/')
def hello():
    return "REST API for FertilityCare data"

@application.route('/', method='OPTIONS')
def trigger_method_options():
    return 0

@application.route('/', method='POST')
def process():
    pprint(request.json)
    action = request.json['action']
    print(action)
    credentials = request.json['credentials']
    user_id = login_user(credentials.email, credentials.password)
    response = do_action(action)
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

def login_user(email, password):
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
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
      cursor = cnx.cursor()
      cursor.execute(get_user_query, (config['DB']['db_name'], email, password))
      cursor.close()
      cnx.close()
    return 1

def do_action(action):
    return {
       'GetData': get_data(),
       'SetData': set_data()
    }.get(action, unknown_action())

def get_data():
    return {}

def set_data():
    return {}

def unknown_action():
    return bottle.HTTPResponse(status=500, body='Unknown action')

run(host='localhost', port=1234, debug=True)


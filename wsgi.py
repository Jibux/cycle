#!/usr/bin/python3


import os
os.chdir(os.path.dirname(__file__))
from bottle import app, run, post, request, response, get, route, template
import bottle
import json
from pprint import pprint

application = bottle.app()


@application.route('/')
def hello():
    return "REST API for FertilityCare data"

@application.route('/', method='OPTIONS')
def trigger_method_options():
    return 0

@application.route('/', method='POST')
def process():
    json_data = request.json['data']
    #print(json_data)
    #j = json.loads(json_data)
    #print(json_data['testdata']);
    return 'OK'
 
#run(host='localhost', port=1234, debug=True)


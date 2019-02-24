#!/usr/bin/python3


import os
os.chdir(os.path.dirname(__file__))
import bottle
from bottle import run, post, request, response, get, route, template
import json
from pprint import pprint
application = bottle.default_app()

from bottle import route
@route('/')
def hello():
    return "Hello World!"

@route('/', method='OPTIONS')
@route('/', method='POST')
def process():
    if request.method == 'OPTIONS':
        print("options")
        response.set_header('Access-Control-Allow-Origin', '*')
        response.set_header('Access-Control-Allow-Method', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        response.set_header('Access-Control-Allow-Headers', 'X-Requested-With,content-type')
        response.set_header('Access-Control-Allow-Credentials', 'true')
        return

    json_data = request.json['data']
    print(json_data)
    #j = json.loads(json_data)
    print(json_data['testdata']);
    return 'OK'
 

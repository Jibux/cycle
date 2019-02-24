#!/usr/bin/python3


import subprocess
#import bottle
from bottle import run, post, request, response, get, route, template
import json
from pprint import pprint


#def enable_cors(fn):
#    def _enable_cors(*args, **kwargs):
#        # set CORS headers
#        response.headers['Access-Control-Allow-Origin'] = '*'
#        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
#        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
#
#        if bottle.request.method != 'OPTIONS':
#            # actual request; reply with the actual response
#            print("return no options")
#            return fn(*args, **kwargs)
#
#    print("return options")
#    return _enable_cors
#
#app = bottle.app()

#@app.route('/', method=['POST, OPTIONS'])
#@enable_cors
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
    
    #return template('Hello {{name}}, how are you?', name=name)
    #return subprocess.check_output(['python',path+'.py'],shell=True)

run(host='localhost', port=1234, debug=True)

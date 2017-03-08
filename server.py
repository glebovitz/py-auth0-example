import jwt
import os

import yaml
from functools import wraps
from flask import Flask, request, jsonify, session, _app_ctx_stack
from flask_session import Session
from flask_cors import cross_origin

def setServiceConfig(required, service, key, env):
    if os.environ.get(env) != None:
        if not service in app.config['services']:
            app.config['services'][service] = {}
        print('Configure Service {1} key {2} env {3}', service, key, env)
        app.config['services'][service][key] = os.environ.get(env)
    elif required and not (service in app.config['services'] and key in app.config['services'][service]):
        print("Service: '{0}' must include key: '{1}'".format(service, key))
        exit()


class RedisConnection:

    connection = None

    def __init__(self, connect = False):
        '''
        Configure settings and initialize connection & db
        '''
        self.config = {
            'redis' : {
                'url' : None,
                'database' : 0,
                'host' : None,
                'port' : None,
                'username' : None,
                'password' : None
             }
        }
        self.r = None

        # Set Mongo connection from with environment variables

        self.config['redis']['url'] = app.config['services']['redis']['url']
        if 'database' in app.config['services']['redis']:
            self.config['redis']['database'] = app.config['services']['redis']['database']

        url = self.config['redis']['url'].replace('redis://', '')
        if '@' in url:
            urlparts = url.split('@')
            login = urlparts[0].split(':')
            url = urlparts[1]
            self.config['redis']['username'] = login[0] if self.config['redis']['username'] is None else None
            self.config['redis']['password'] = login[1] if self.config['redis']['password'] is None else None
        if ':' in url:
            urlparts = url.split(':')
            self.config['redis']['host'] = urlparts[0] if self.config['redis']['host'] is None else None
            self.config['redis']['port'] = urlparts[1] if self.config['redis']['port'] is None else None
        print ("host {0}, port {1}, user {2}, pass {3} ",
            self.config['redis']['host'],
            self.config['redis']['port'],
            self.config['redis']['username'],
            self.config['redis']['password'])
        if connect:
            self.connect()
        RedisConnection.connection = self

    def connect(self):
        '''
        Connect to Redis datastore connection.
        '''
        import redis
        self.r = redis.Redis(
            host     = self.config['redis']['host'],
            port     = self.config['redis']['port'],
            db       = self.config['redis']['database'],
            password = self.config['redis']['password']
        )

        return self

    def set_app_config_for_sessions(self, app_config_dict):
        app_config_dict['SESSION_REDIS'] = self.r
        return self


app = Flask(__name__)
app.config['services'] = {}

setServiceConfig(True,  'flask',     'ip',   'AUTH0_SERVICE_IP')
setServiceConfig(True,  'flask',     'port',  'AUTH0_SERVICE_PORT')
setServiceConfig(True,  'auth0',     'id',   'AUTH0_CLIENT_ID')
setServiceConfig(True,  'auth0',     'key',  'AUTH0_CLIENT_SECRET')
setServiceConfig(True,  'redis',     'url', 'REDIS_DB_URL')
setServiceConfig(False, 'redis',     'database', 'REDIS_DB_DB')

app.config['redis'] = RedisConnection(True).set_app_config_for_sessions(app.config)
app.config['SESSION_TYPE'] = 'redis'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 60 # 2 months
Session(app)

# Format error response and append status code.
def handle_error(error, status_code):
    resp = jsonify(error)
    resp.status_code = status_code
    return resp

client_id = app.config['services']['auth0']['id']
client_key = app.config['services']['auth0']['key']

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # auth = request.headers.get('Authorization', None)
        # if not auth:
        #     return handle_error({'code': 'authorization_header_missing',
        #                         'description':
        #                             'Authorization header is expected'}, 401)
        #
        # parts = auth.split()
        #
        # if parts[0].lower() != 'bearer':
        #     return handle_error({'code': 'invalid_header',
        #                         'description':
        #                             'Authorization header must start with'
        #                             'Bearer'}, 401)
        # elif len(parts) == 1:
        #     return handle_error({'code': 'invalid_header',
        #                         'description': 'Token not found'}, 401)
        # elif len(parts) > 2:
        #     return handle_error({'code': 'invalid_header',
        #                         'description': 'Authorization header must be'
        #                          'Bearer + \s + token'}, 401)
        #
        # token = parts[1]
        # try:
        #     payload = jwt.decode(
        #         token,
        #         client_secret,
        #         audience=client_id
        #     )
        # except jwt.ExpiredSignature:
        #     return handle_error({'code': 'token_expired',
        #                         'description': 'token is expired'}, 401)
        # except jwt.InvalidAudienceError:
        #     return handle_error({'code': 'invalid_audience',
        #                         'description': 'incorrect audience, expected: '
        #                          + client_id}, 401)
        # except jwt.DecodeError:
        #     return handle_error({'code': 'token_invalid_signature',
        #                         'description':
        #                             'token signature is invalid'}, 401)
        # except Exception:
        #     return handle_error({'code': 'invalid_header',
        #                         'description': 'Unable to parse authentication'
        #                          ' token.'}, 400)
        #
        # _app_ctx_stack.top.current_user = payload
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route("/ping")
@cross_origin(headers=['Content-Type', 'Authorization'])
def ping():
    return "All good. You don't need to be authenticated to call this"


@app.route("/secured/ping")
@cross_origin(headers=['Content-Type', 'Authorization'])
@cross_origin(headers=['Access-Control-Allow-Origin', '*'])
@requires_auth
def securedPing():
    return "All good. You only get this message if you're authenticated"

#port 3001
print ("start ip = {0}, port = {1}", app.config['services']['flask']['ip'], app.config['services']['flask']['port'])
if __name__ == "__main__":
    app.run(host=app.config['services']['flask']['ip'], port=app.config['services']['flask']['port'])

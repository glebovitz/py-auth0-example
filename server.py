import jwt
import os

import yaml
from functools import wraps
from flask import Flask, request, jsonify, session, _app_ctx_stack
from dotenv import Dotenv
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

app = Flask(__name__)
app.config['services'] = {}

setServiceConfig(True,  'auth0',     'id',   'AUTH0_CLIENT_ID')
setServiceConfig(True,  'auth0',     'key',  'AUTH0_CLIENT_SECRET')

# Format error response and append status code.
def handle_error(error, status_code):
    resp = jsonify(error)
    resp.status_code = status_code
    return resp


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 3001))
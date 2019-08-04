import json
import logging
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt import JWT, jwt_required

from cms import aws_account_manager as account_manager
from cms import github
from cms import validator



logging.getLogger().setLevel(logging.INFO)
app = Flask(__name__)
CORS(app)

    

@app.route('/auth/login', methods=['POST'])
def login():

    data = request.get_json()

    # authenticate the user
    email = data["email"]
    password = data["password"]

    accountmgr = account_manager.AccountManager()
    jwt = accountmgr.login(email, password)

    if (jwt is not None):
        # print ("logged in:", jwt)
        return jsonify(jwt), 200
    else:
        print ("log in errored")
        return jsonify(validator.validation_authentication_failed()), 401


@app.route('/auth/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    # reset the password
    email = data["email"];
    password = data["password"];
    reset_code = data["reset_code"];

    # if the reset code is valid and not expired, 
    # then change the account password to the one provided
    pass


@app.route('/auth/forgot', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    
    # send forgot password email with temp key
    email = data["email"];
    reset_code = "generate a uuid key";

    # email the customer a link to a page to reset their password
    pass


@app.route('/auth', methods=['DELETE'])
def logout():
    data = request.get_json()
    
    
    # remove the current session to log out the user
    token = req.get_header("x-auth-token")

    # remove the session object from the cache.

    # return ok
    return

@app.route('/accounts', methods=['POST'])
def accounts():
    accountmgr = account_manager.AccountManager()

    data = request.get_json()


    if (data.get("confirmation_code") is not None):
        email = data["email"];
        confirmation_code = data["confirmation_code"]
        accountmgr.user_confirm_signup(email, confirmation_code)
        
        return jsonify({}), 200

    else:
        email = data["email"];
        password = data["password"];

         # validate the fields are correct formatted
        result = validator.validate_signup(email, password);

        if (len(result) == 0):
            jwt = accountmgr.signup(email, password)

            return jsonify(jwt), 201

        else:
            return jsonify(result), 400


@app.route('/git/<path:url>', methods=['GET'])
def gitproxy(url):
    # proxy the call to github
    git = github.Client()
    r = git.proxy(url)

    try:
        json_object = r.json()
        return jsonify(json_object), r.status_code

    except ValueError:
        return r.text, r.status_code


@app.route('/', methods=['GET'])
def homedoc():

    doc = {
        "api": {
          "title": "CMS"
        }
      }

    return jsonify(doc);



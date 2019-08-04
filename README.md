CMS
==========

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/drawbuildplay/seo_report/master/LICENSE)

How Stuff Works
--------------------------------------------

1.  Authentication is handled by the cms/aws_account_manager.py Module.  This module interacts with AWS Cognito to register users, and provide authentication.  

If you want to build a handler for a different JWT auth provider, implement a module with the same interface, and import that into the flask_api.py.

2. Content is stored in a github repo in Markdown where your Hugo website resides.  If you want to integrate with Gitlab or Bitbucket or something else, implement your own github_storage.py Module with the same interface and import that into the flask_api.py.



Create your User Pool in AWS Cognito
--------------------------------------------

Create a new User Pool (or open an existing User Pool) for your CMS users.

Create an App Client for the CMS API to connect with to Cognito.

Take note of the Client ID and Secret and User Pool ID.  You will use them to configure your CMS App.



Installing locally as a REST API (Flask)
------------------------------

```
virtualenv venv
source venv/bin/activate

cd cms
pip install -r requirements.txt
```

Setup your local environment configurations
--------------------------------------------

Create a file `config.sh` 

Paste the following config settings into it, and set appropriately for your local environment.

```
#!/bin/bash
export AWS_COGNITO_CLIENT_ID="<YOUR COGNITO APP CLIENT ID>"
export AWS_COGNITO_CLIENT_SECRET="<YOUR COGNITO APP CLIENT SECRET>"
export AWS_COGNITO_USER_POOL_ID="<YOUR COGNITO USER POOL ID>"
export AWS_COGNITO_REGION="us-east-1"
export GITHUB_TOKEN=""
export GITHUB_OWNER=""
export GITHUB_REPO=""
```

Source the script locally to set your environment variables for the app to use.

```
	source config.sh
```

Note - for zappa deployment purposes, these variables are also defined in the `zappa_settings.json` file.

Running locally as a REST API (Flask)
------------------------------

Change into the nested `cms` folder
```
cd cms
```

On Unix based systems that support gunicorn, run:
```
gunicorn app:api --bind 127.0.0.1:8001
```

Alternatively (eg on Windows where gunicorn is not supported) you can run directly using Flask 
```
flask run -h 127.0.0.1 -p 8001
```


Test the API is running correctly by retrieving the home doc:
```
curl -X GET 'http://127.0.0.1:8001/'
```

Deploying to AWS Lambda with Zappa
-------------------------

Configure your `zappa_settings.json` file:

```
{
    "prod": {
		"app_function": "cms.flask_api.app",
		"aws_region": "us-east-1",
		"profile_name": "default",
		"project_name": "cms",
		"runtime": "python3.7",
		"s3_bucket": "zappa-cms",
		"certificate_arn": "",
		"domain": "cms.thediyblogger.com",
		"extra_permissions": [{ // Attach any extra permissions to this policy.
		    "Effect": "Allow",
		    "Action": ["cognito-idp:*"], // AWS Service ARN
		    "Resource": "*"
		}],
		"environment_variables": {
            "AWS_COGNITO_CLIENT_ID": "",
            "AWS_COGNITO_CLIENT_SECRET": "",
            "AWS_COGNITO_USER_POOL_ID": "",
            "AWS_COGNITO_REGION": "us-east-1",
            "GITHUB_TOKEN": "",
            "GITHUB_OWNER": "",
            "GITHUB_REPO": ""
        }
    }
}
```

Then deploy your application to AWS Lambda.  This will set up the API Gateway to your Lambda functions also.
```
zappa deploy prod
zappa update
```


Testing
-------
```
pip install -r tests/test-requirements.txt
nosetests --with-coverage
```

import base64
import boto3
import botocore
import json
import hmac
import hashlib
import logging
import os
import string
import random
import requests
import time

from jose import jwk, jwt
from jose.utils import base64url_decode



class AccountManager(object):

	client = None
	CLIENT_ID = os.environ.get("AWS_COGNITO_CLIENT_ID")
	CLIENT_SECRET = os.environ.get("AWS_COGNITO_CLIENT_SECRET")
	USER_POOL_ID = os.environ.get("AWS_COGNITO_USER_POOL_ID")
	REGION = os.environ.get("AWS_COGNITO_REGION")

	# instead of re-downloading the public keys every time
	# we download them only on cold start
	# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
	keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(REGION, USER_POOL_ID)
	response = requests.get(keys_url)
	keys = response.json()['keys']


	def __init__(self):
		self.client = boto3.client('cognito-idp')


	def decode_verify_jwt_token(self, jwt_token):
		# copied from https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py

		token = jwt_token

		# get the kid from the headers prior to verification
		headers = jwt.get_unverified_headers(token)
		kid = headers['kid']

		# search for the kid in the downloaded public keys
		key_index = -1
		for i in range(len(self.keys)):
		    if kid == self.keys[i]['kid']:
		        key_index = i
		        break
		if key_index == -1:
		    logging.warning('Public key not found in jwks.json')
		    return False

		# construct the public key
		public_key = jwk.construct(self.keys[key_index])

		# get the last two sections of the token,
		# message and signature (encoded in base64)
		message, encoded_signature = str(token).rsplit('.', 1)

		# decode the signature
		decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

		# verify the signature
		if not public_key.verify(message.encode("utf8"), decoded_signature):
		    logging.warning('Signature verification failed')
		    return False
		# print('Signature successfully verified')

		# since we passed the verification, we can now safely
		# use the unverified claims
		claims = jwt.get_unverified_claims(token)

		# additionally we can verify the token expiration
		if time.time() > claims['exp']:
		    logging.warning('Token is expired')
		    return False

		# and the Audience  (use claims['client_id'] if verifying an access token)
		if claims['aud'] != self.CLIENT_ID:
		    logging.warning('Token was not issued for this audience')
		    return False

		# now we can use the claims
		# print(claims)
		return claims

	def get_secret_hash(self, username):
		# A keyed-hash message authentication code (HMAC) calculated using
		# the secret key of a user pool client and username plus the client
		# ID in the message.
		message = username + self.CLIENT_ID
		dig = hmac.new(
			bytes(self.CLIENT_SECRET, 'latin-1'),
			bytes(message, 'latin-1'),
		    hashlib.sha256).digest()

		return base64.b64encode(dig).decode()

	'''
	def generate_password(self, stringLength=10):
		"""Generate a random password """

		randomSource = string.ascii_letters + string.digits + string.punctuation
		password = random.choice(string.ascii_lowercase)
		password += random.choice(string.ascii_uppercase)
		password += random.choice(string.digits)
		password += random.choice(string.punctuation)

		for i in range(stringLength - 4):
		    password += random.choice(randomSource)

		passwordList = list(password)
		random.SystemRandom().shuffle(passwordList)

		password = ''.join(passwordList)

		return password
	'''

	def signup(self, email, password):

		# signup the user with Cognito
		# Return a digest for the message.
		secrethash = self.get_secret_hash(email)

        # TODO: the pinterest token should really be stored in aws:secret store instead of the JWT token.
		create_response = self.client.sign_up(
			ClientId=self.CLIENT_ID,
			SecretHash=secrethash,
			Username=email,
			Password=password,
			UserAttributes=[
				{
				    'Name': 'email',
				    'Value': email
				}
			]
		)

		# automatically verify the account.  
		# The user should verify their email properly later on to make signup easier.
		self.admin_confirm_signup(email)

		# log the user in
		session = self.login(email, password)

		return session;

	def user_confirm_signup(self, email, confirmation_code):
		
		response = self.client.confirm_sign_up(
				ClientId=self.CLIENT_ID,
				SecretHash=self.get_secret_hash(email),
				Username=email,
				ConfirmationCode=confirmation_code,
				ForceAliasCreation=False
			)

	def admin_confirm_signup(self, email):
		
		response = self.client.admin_confirm_sign_up(
				UserPoolId=self.USER_POOL_ID,
			    Username=email
		    )


	def login(self, email, password):
		try:
			response = self.client.initiate_auth(
				AuthFlow='USER_PASSWORD_AUTH',
			    AuthParameters={
			        'USERNAME': email,
			        'PASSWORD': password,
			        'SECRET_HASH': self.get_secret_hash(email)
			    },
			    ClientId=self.CLIENT_ID
			)

			print ("Login: ", response)

			session = { 
				"token": response["AuthenticationResult"]["IdToken"],
				"expires": response["AuthenticationResult"]["ExpiresIn"]
			} 

			# create a session with this access token as the key
			return session

		except self.client.exceptions.UserNotFoundException:
			return None

	def find_account(self, email):
		try:
			response = self.client.admin_get_user(
			    UserPoolId=self.USER_POOL_ID,
			    Username=email
			)

			return response

		except self.client.exceptions.UserNotFoundException:
			return None


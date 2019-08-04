
import re
import string

from cms import aws_account_manager as account_manager

def log_message(list, field, message):
	list.append({
		"field": field,
		"message": message
	});

def validation_authentication_failed():
	results = []

	log_message(results, "email", "Log in failed.")

	return results

def validation_token_failed():
	results = []

	log_message(results, "token", "Authentication Token is not valid.")

	return results

def validate_signup(email, password):
	results = []

	results.extend(validate_email(email))
	results.extend(validate_password(password))
	results.extend(validate_unique_account(email))

	return results


def validate_email(email):
	EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
	match = EMAIL_REGEX.match(email)

	results = []
	if not match:
		log_message(results, "email", "Please enter a valid email address.")
		

	return results

def validate_password (password):
	results = []


	if len(password) < 8:
		log_message(results, "password", "Make sure your password is at least 8 characters.")
	
	if not any(char.isdigit() for char in password): 
		log_message(results, "password", "Make sure your password has a number in it.")
	
	if not any(char.isupper() for char in password): 
		log_message(results, "password", "Make sure your password has a lowercase letter in it.")
	
	if not any(char.islower() for char in password): 
		log_message(results, "password", "Make sure your password has an uppercase letter in it.")
	
	special_symbol =['$', '@', '#', '%', '!', '%', '^', '&', '*', '(', ')', '-', '+'] 
	if not any(char in special_symbol for char in password): 
		log_message(results, "password", "Make sure your password has a special character in it.")

	return results


def validate_domain(domain):
	regex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	match = re.match(regex, domain)

	results = []
	if not match:
		log_message(results, "domain", "Please enter a valid domain (e.g. 'https://www.mydomain.com')")
		

	return results


def validate_unique_account(email):
	am = account_manager.AccountManager()

	account = am.find_account(email)

	results = []
	if account is not None:
		log_message(results, "email", "An account already exists with this email address. Try logging in instead if you already have an account.")

	return results
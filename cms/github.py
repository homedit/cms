import json
import logging
import os
import requests


class Client(object):

	api_token = None
	owner = None
	github_base_url = None

	def __init__(self):
	
		self.api_token = os.environ.get("GITHUB_TOKEN")
		self.owner = os.environ.get("GITHUB_OWNER")
		self.repo = os.environ.get("GITHUB_REPO")

		github_api = "https://api.github.com/repos/{0}/{1}/"
		self.github_base_url = github_api.format(self.owner, self.repo)



	def proxy(self, url):
		headers = self._get_headers()
		url = self._generate_proxy_url(url)

		logging.info("url:{0}, headers:{1}".format(url, headers))
		r = requests.get(url, headers=headers)

		return r


	def _get_headers(self):
		headers = {
			"Authorization": "token {0}".format(self.api_token),
			"Accept": "application/vnd.github.v3.raw+json"
			}

		return headers

	def _generate_proxy_url(self, url):
		url = "{0}{1}".format(self.github_base_url, url)
		return url

	
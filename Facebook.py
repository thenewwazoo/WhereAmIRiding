import urllib
import urlparse
from anticsrf import csrf_token, csrf_protected
import web
from settings import WIAR
import json

import logging

def is_current_user_admin():
	return False

def create_logout_url(redirect_url):
	logout_url = "https://www.facebook.com/logout.php?%s"
	logout_params = urllib.urlencode({
		'next': redirect_url,
		'access_token': web.ctx.session['access_token']
		})
	return logout_url % logout_params

def create_login_url(redirect_url):
	dialog_url = "https://www.facebook.com/dialog/oauth?%s"
	dialog_args = urllib.urlencode({
		'client_id': WIAR.Facebook.app_id,
		'redirect_uri': redirect_url,
		'state': csrf_token(),
		'scope': "email"
	})
	return dialog_url % dialog_args

def get_current_user():
	if web.ctx.session.has_key('access_token'):
		return _build_user(web.ctx.session['access_token'])

	req_data = web.input(code="nocode")
	if req_data.code == "nocode":
		return None
	logging.info("code is %s" % req_data.code)

	return _get_access_token(req_data.code)

def _build_user(access_token):

	graph_url = "https://graph.facebook.com/me?%s"
	graph_args = urllib.urlencode({
		'access_token': access_token
		})

	userinfo = json.load( urllib.urlopen(graph_url % graph_args) )
	if 'error' in userinfo:
		return None

	return FBUser(userinfo)

@csrf_protected
def _get_access_token(code):

	token_url = "https://graph.facebook.com/oauth/access_token?%s"
	token_args = urllib.urlencode({ 
		'client_id': WIAR.Facebook.app_id, 
		'redirect_uri': web.ctx.home + web.ctx.path, # NOTE: web.ctx.home is just a convenient value - it may not be right! 
		'client_secret': WIAR.Facebook.app_secret,
		'code': code
		})

	logging.info("getting token with url %s" % (token_url % token_args))
	rawresp = urllib.urlopen( token_url % token_args ).read()
	logging.info("rawresp was %s" % rawresp)
	token_response = urlparse.parse_qs( rawresp )
	logging.info("resp was %s" % token_response)
	if 'access_token' not in token_response or 'expires' not in token_response:
		#return None
		raise BaseException("fail")

	access_token = token_response['access_token'][0] # From the urlparse.parse_qs documentation:
	token_expiry = token_response['expires'][0]      #  "The dictionary keys are the unique query variable names and the values are lists of values for each name."
	web.ctx.session['access_token'] = access_token

	return _build_user(access_token)

class FBUser(object):
	def __init__(self, jsonObj):
		self.jsonData = jsonObj

	def user_id(self):
		# return the unique userid used to identify users in the db
		# equivalent to the google users' UID not, e.g., an email address
		return self.jsonData['id']

	def nickname(self):
		return self.jsonData['name']

	def email(self):
		return self.jsonData['email']


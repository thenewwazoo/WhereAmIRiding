import logging

login_mechanisms = {
	"Facebook": "loginmethods.Facebook",
	"Google": "google.appengine.api.users"
}

def loginmethod(mechanism):
	try:
		mod = __import__(login_mechanisms[mechanism], fromlist=["users"])
	except ImportError:
		raise
	return mod

def get_login_strings(base_url):
	outdict = {}
	for provider in login_mechanisms.keys():
		url = base_url + provider
		outdict[provider] = url
	return outdict
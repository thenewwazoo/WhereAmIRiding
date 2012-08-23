import loginmethods

from datamodels import SPOTUser
from GoogleStore import GoogleStore

import web
from anticsrf import csrf_token, csrf_protected

import logging

urls = (

	'/register/(.*)/?', 'RegHandler',
	'/logout/*', 'LogoutHandler'
)

dataform = SPOTUser.buildForm()

app = web.application(urls, locals())
registration_app = app.wsgifunc()
session = web.session.Session(app, GoogleStore('WIAR'))

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))

render = web.template.render('templates/', globals={'csrf_token': csrf_token})

class LogoutHandler:
	def GET(self):
		url = "/"
		users = _get_login_method()
		if users is not None:
			url = users.create_logout_url(web.ctx.home) # we need to do single sign-out for our providers
			del web.ctx.session['loginprovider']
		if web.ctx.session.has_key('access_token'): # for Facebook auth FIXME
			del web.ctx.session['access_token']
		raise web.seeother( url )

class RegHandler:
	def GET(self, loginMethod):
		web.header("Cache-Control", "no-store, no-cache, must-revalidate")

		if not web.ctx.session.has_key('loginprovider'): # we don't have a preferred provider stored
			if not loginMethod: # and we don't see one specified in the query
				return _to_provider_selection() # ask which login method to use
			else:
				web.ctx.session['loginprovider'] = loginMethod

		users = _get_login_method()
		if users is None:
			return "Invalid login mechanism"

		user = users.get_current_user()
		logging.info("user is %s" % repr(user))
		if not user: # user is not logged in. forward to login page, with breadcrumb
			raise web.seeother( users.create_login_url(web.ctx.home + web.ctx.path), absolute=True)
		userrec = SPOTUser.get_by_key_name(user.user_id())
		regform = dataform()
		if userrec is not None:
			from google.appengine.ext import db
			regform.fill( db.to_dict(userrec) )
		return render.registration(user.nickname(), regform, "/logout/")

	@csrf_protected
	def POST(self, loginMethod): # we ignore the loginMethod paramter
		users = _get_login_method()
		if users is None:
			raise web.seeother(web.ctx.home + web.ctx.path)
		user = users.get_current_user()
		if not user:
			raise web.seeother( users.create_login_url( "/" ) )
		regform = dataform()
		if not regform.validates():
			return render.registration(user.email(), regform, users.create_logout_url("/"))
		else:
			# if the user left an optional field blank, we have to blow it away, in order to skip db.Model validation
			formdata = regform.d
			for key in formdata.keys():
				if formdata[key] == "":
					del formdata[key]
			userrec = SPOTUser(key_name=user.user_id(), **formdata)
			userrec.put()
			raise web.seeother( "/" )

def _get_login_method():
	if web.ctx.session.has_key('loginprovider'):
		try:
			return loginmethods.loginmethod(web.ctx.session['loginprovider'])
		except ImportError:
			del web.ctx.session['loginprovider']
			return None
	else:
		return None

def _to_provider_selection():
	return render.login( loginmethods.get_login_strings(web.ctx.home + web.ctx.path) )
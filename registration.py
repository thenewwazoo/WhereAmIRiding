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
		auth_engine = _get_login_method()
		if auth_engine is not None:
			url = auth_engine.create_logout_url(web.ctx.home) # we need to do single sign-out for our providers
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

		auth_engine = _get_login_method()
		if auth_engine is None:
			return "Invalid login mechanism"

		user = auth_engine.get_current_user()
		logging.info("user is %s" % repr(user))
		if not user: # user is not logged in. forward to login page, with breadcrumb
			raise web.seeother( auth_engine.create_login_url(web.ctx.home + web.ctx.path), absolute=True)
		userrec = SPOTUser.get_by_key_name(user.user_id())
		regform = dataform()
		if userrec is not None:
			from google.appengine.ext import db
			regform.fill( db.to_dict(userrec) )
			regform['userDispName'].attrs['readonly'] = "readonly"
		return _to_data_form(user, regform=regform)

	@csrf_protected
	def POST(self, loginMethod): # we ignore the loginMethod paramter

		auth_engine = _get_login_method()
		if auth_engine is None:
			raise web.seeother(web.ctx.home + web.ctx.path)
		user = auth_engine.get_current_user()
		if not user:
			raise web.seeother( auth_engine.create_login_url( "/" ) )

		regform = dataform()
		if not regform.validates():
			return _to_data_form(user, regform=regform)
		else:
			# if the user left an optional field blank, we have to blow it away, in order to skip db.Model validation
			formdata = regform.d
			for key in formdata.keys():
				if formdata[key] == "":
					del formdata[key]

			# if this user's saved info before, find it
			userrec = SPOTUser.get_by_key_name(user.user_id())
			if userrec is not None:
				del formdata['userDispName'] # we don't allow users to alter their display names, once set
			else:
				dispname_colltest = SPOTUser.all().filter('userDispName =', formdata['userDispName']).get()
				if dispname_colltest is not None and userrec.key() != dispname_colltest.key():
					return _to_data_form(user, regform=regform, dispname_coll=True)
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

def _to_data_form(user, regform=dataform(), dispname_coll=None):
	return render.registration(user.nickname(), regform, "/logout/", dispname_coll)
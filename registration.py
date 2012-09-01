import loginmethods

from datamodels import SPOTUser
from GoogleStore import GoogleStore

import web
from anticsrf import csrf_token, csrf_protected

import logging

urls = (

	'/register/(.*)/?', 'RegHandler',
	'/logout/*', 'LogoutHandler',
	'/userimage/(.*)/', 'UserImageHandler'
)

dataform = SPOTUser.buildForm()

app = web.application(urls, locals())
registration_app = app.wsgifunc()
session = web.session.Session(app, GoogleStore('WIAR'))

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))

render = web.template.render('templates/', globals={'csrf_token': csrf_token})

class UserImageHandler:
	def GET(self, userkey):
		logging.info("requested image for userkey %s" % userkey)
		try:
			userrec = SPOTUser.get(userkey)
			if userrec.userImage is None:
				web.seeother("http://www.whereamiriding.com/gpsfiles/map/images/motorcycle2.png") # FIXME
			web.header('Content-Type', 'image/png')
			return userrec.userImage
		except:
			return "No Image"

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

		regform = dataform()

		auth_engine = _get_login_method()
		if auth_engine is None:
			return "Invalid login mechanism"

		user = auth_engine.get_current_user()
		logging.info("user is %s" % repr(user))
		if not user: # user is not logged in. forward to login page, with breadcrumb
			raise web.seeother( auth_engine.create_login_url(web.ctx.home + web.ctx.path), absolute=True)
		userrec = SPOTUser.get_by_key_name(user.user_id())
		if userrec is not None:
			from google.appengine.ext import db
			regform.fill( db.to_dict(userrec) )
			regform['userDispName'].attrs['readonly'] = "readonly"
			return _to_data_form(user, regform=regform, hasimage=userrec.key())

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
			logging.info("form did not validate")
			return _to_data_form(user, regform=regform)
		else:
			# if the user left an optional field blank, we have to blow it away, in order to skip db.Model validation
			formdata = regform.d
			for key in formdata.keys():
				if formdata[key] == "":
					del formdata[key]

			# FIXME this is pretty hacky. replace with something more elegant, maybe
			#  as part of abstracting out the storage layer. that'd be nice.

			# if this user's saved info before, find it
			oldrec = SPOTUser.get_by_key_name(user.user_id())
			if oldrec is not None:
				# we don't allow users to alter their display names, once set
				formdata['userDispName'] = oldrec.userDispName
			else: # this is a new user
				dispname_colltest = SPOTUser.all().filter('userDispName =', formdata['userDispName']).get()
				if dispname_colltest is not None and oldrec.key() != dispname_colltest.key():
					return _to_data_form(user, regform=regform, dispname_coll=True)

			userrec = SPOTUser(key_name=user.user_id(), **formdata)
			try:
				from google.appengine.api import images
				from google.appengine.ext import db
				if regform['userImage'].value == "":
					userrec.userImage = oldrec.userImage
				else:
					avatar = images.resize(regform['userImage'].value, 250, 250)
					userrec.userImage = db.Blob(avatar)
			except images.NotImageError:
				pass
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

def _to_data_form(user, regform=dataform(), dispname_coll=None, hasimage=None):
	# if regform is not pristine, clear out the userImage data
	regform['userImage'].set_value("")
	return render.registration(user.nickname(), regform, "/logout/", dispname_coll, hasimage)
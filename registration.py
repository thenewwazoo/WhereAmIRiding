#from google.appengine.api import users
import Facebook as users

from datamodels import SPOTUser
from GoogleStore import GoogleStore

import web
from anticsrf import csrf_token, csrf_protected

urls = (
	'/register/*', "RegHandler"
)

dataform = SPOTUser.buildForm()

app = web.application(urls, locals())
registration_app = app.wsgifunc()
session = web.session.Session(app, GoogleStore('WIAR'))

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))

render = web.template.render('templates/', globals={'csrf_token': csrf_token})

class RegHandler:
	def GET(self):
		web.header("Cache-Control", "no-store, no-cache, must-revalidate")
		user = users.get_current_user()
		if not user: # user is not logged in. forward to login page, with breadcrumb
			raise web.seeother( users.create_login_url(web.ctx.home + web.ctx.path), absolute=True)
		userrec = SPOTUser.get_by_key_name(user.user_id())
		regform = dataform()
		if userrec is not None:
			from google.appengine.ext import db
			regform.fill( db.to_dict(userrec) )
		return render.registration(user.email(), regform, users.create_logout_url("/"))

	@csrf_protected
	def POST(self):
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

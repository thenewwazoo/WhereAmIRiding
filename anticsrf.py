
import web
from GoogleStore import GoogleStore

# pass to render object like so:
# render = web.template.render('templates/', globals={'csrf_token':csrf_token})

def csrf_token():
	"""Should be called from the form page's template:
	<form method=post action="">
 		<input type=hidden name=state value="$csrf_token()">
		...
	</form>"""
	if not web.ctx.session.has_key('state'):
		from uuid import uuid4
		web.ctx.session['state'] = uuid4().hex
	return web.ctx.session['state']

def csrf_protected(f):
	"""Usage:
	   @csrf_protected
	   def POST(self):
		   ..."""
	def decorated(*args,**kwargs):
		inp = web.input()
		if not ( inp.has_key('state') and inp.state == web.ctx.session.pop('state', None) ):
			raise web.HTTPError(
				"400 Bad request",
				{'content-type':'text/html'},
				'Bad request')
 
		return f(*args,**kwargs)
	return decorated


import web

# pass to render object like so:
# render = web.template.render('templates/', globals={'csrf_token':csrf_token})

def csrf_token():
	"""Should be called from the form page's template:
	<form method=post action="">
 		<input type=hidden name=csrf_token value="$csrf_token()">
		...
	</form>"""
	if not web.cookies().get('csrf_token'):
		from uuid import uuid4
		web.setcookie('csrf_token', uuid4().hex, 1800)
	return web.cookies().get('csrf_token')

def csrf_protected(f):
	"""Usage:
	   @csrf_protected
	   def POST(self):
		   ..."""
	def decorated(*args,**kwargs):
		inp = web.input()
		if not (inp.has_key('csrf_token') and inp.csrf_token==web.cookies().get('csrf_token')):
			raise web.HTTPError(
				"400 Bad request",
				{'content-type':'text/html'},
				'Bad request')
 
		return f(*args,**kwargs)
	return decorated
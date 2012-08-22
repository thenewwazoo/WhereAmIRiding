import web
from google.appengine.ext import db
try:
    import cPickle as pickle
except ImportError:
    import pickle
import datetime

CLEANUP_BATCH_SIZE = 20

class WebpySession(db.Model):
    data = db.BlobProperty()
    atime = db.DateTimeProperty(auto_now=True)

class GoogleStore(web.session.Store):
    """Google Datastore"""
    def __init__(self, prefix="p"):
        self.prefix=prefix

    def __contains__(self, key):
        return WebpySession.get_by_key_name(self.prefix+key) is not None

    def __getitem__(self, key):
        try:
            return pickle.loads(WebpySession.get_by_key_name(self.prefix+key).data)
        except AttributeError:
            raise KeyError, key

    def __setitem__(self, key, value):
        r = WebpySession.get_or_insert(self.prefix+key)
        r.data = pickle.dumps(value)
        r.put()

    def __delitem__(self, key):
        try:
            WebpySession.get_by_key_name(self.prefix+key).delete()
        except AttributeError:
            pass

    def cleanup(self, timeout):
        db.delete(WebpySession.all().filter('atime <', datetime.datetime.now()-datetime.timedelta(seconds=timeout)).fetch(CLEANUP_BATCH_SIZE))

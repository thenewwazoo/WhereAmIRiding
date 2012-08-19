#!/usr/bin/env python

import web

from google.appengine.ext import db

from datamodels import SPOTUser

render = web.template.render('templates/')

urls = (
    '/(.*)/', 'index',
    '/(.*)', 'index',
    '/', 'index'
)

class index:
    def GET(self, riderid):
        if riderid == "":
            return "No user specified"
            pass
        else:
            userrec = db.Query(SPOTUser).filter('userDispName =', riderid).get()
            if userrec is not None:
                return render.usermap(userrec.userDispName, userrec.userWebsite, userrec.glId)
            else:
                return "User not found"

app = web.application(urls, locals()).wsgifunc()

if __name__ == "__main__":
    app.cgirun()

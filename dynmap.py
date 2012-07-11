#!/usr/bin/env python

import web
import prefs
import ridehistory
import eventinfo

render = web.template.render('templates/')

urls = (
    '/prefs', prefs.prefs_app,
    '/ridehistory', ridehistory.ridehistory_app,
    '/eventinfo', eventinfo.eventinfo_app,
    '/(.*)', 'index',
)

class index:
    def GET(self, riderid):
        ridername = "bmatt the loon"
        return render.map(ridername, riderid)

if __name__ == "__main__":
    app = web.application(urls, locals())
    app.run()

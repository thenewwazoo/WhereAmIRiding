#!/usr/bin/env python

import web
import prefs
import ridehistory
import eventinfo
from cgi import escape

render = web.template.render('templates/')

urls = (
    '/prefs', prefs.prefs_app,
    '/ridehistory', ridehistory.ridehistory_app,
    '/eventinfo', eventinfo.eventinfo_app,
    '/(.*)', 'index',
)

class index:
    def GET(self, riderid):
        if riderid == "":
            #return render.activemap()
            pass
        else:
            riderid = escape(riderid, True)
            riderurl = "http://optimaltour.us/"
            ridername = "bmatt the loon"
            riderglId = "0PYkecaqTzOMoTYm4fJaX5SKdSjhW3i7y"
            return render.usermap(ridername, riderid, riderurl, riderglId)

app = web.application(urls, locals()).wsgifunc()

if __name__ == "__main__":
    app.cgirun()

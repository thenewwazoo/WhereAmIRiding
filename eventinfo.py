#!/usr/bin/env python

import web
import json

render = web.template.render('templates/')

urls = (
  '/eventinfo/(.*)/(.*)', 'eventinfo'
)

eventinfo_app = web.application(urls, locals()).wsgifunc()

class eventinfo:
  def GET(self, riderid, eventid):
    # select (userinfo.username, events.time, events.date, events.lat, events.lng, events.msgtype, events.message)
    #  from userinfo, events
    #  where userinfo.riderid == $riderid and events.riderid == $riderid and events.eventid == $eventid
    username = "bmatt the loon"
    time = "6:55am PST"
    date = "6/28/2012 - Thursday"
    lat = 33.10391
    lng = -117.21759
    msgtype = "OK Button"
    message = "This is a test message that is not dynamic in nature"
    return render.infowindow(username, eventid, time, date, lat, lng, msgtype, message)

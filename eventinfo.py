#!/usr/bin/env python

import web
import json

import logging

from google.appengine.ext import db
from datamodels import SPOTUser, SPOTMessageRecord

render = web.template.render('templates/')

urls = (
  '/eventinfo/(.*)/(.*)/', 'eventinfo'
)

eventinfo_app = web.application(urls, locals()).wsgifunc()

class eventinfo:
  def GET(self, riderid, eventid):
    # select (userinfo.username, events.time, events.date, events.lat, events.lng, events.msgtype, events.message)
    #  from userinfo, events
    #  where userinfo.riderid == $riderid and events.riderid == $riderid and events.eventid == $eventid
    # (...or, y'know, don't use relational DBs)

    logging.info("getinfo %s %s" % (riderid, eventid))

    userrec = SPOTUser.get(db.Key(encoded=riderid))
    eventrec = SPOTMessageRecord.get(db.Key(encoded=eventid))

    username = userrec.userDispName
    timestamp = eventrec.timestamp
    location = eventrec.location
    msgtype = eventrec.messageType
    message = eventrec.messageDetail
    return render.infowindow(username, timestamp, location, msgtype, message)

#!/usr/bin/env python

import web
import json

import logging

from datamodels import SPOTUser, SPOTMessageRecord

render = web.template.render('templates/')

urls = (
  '/eventinfo/(.*)/', 'eventinfo'
)

eventinfo_app = web.application(urls, locals()).wsgifunc()

class eventinfo:
  def GET(self, eventid):
    # select (userinfo.username, events.time, events.date, events.lat, events.lng, events.msgtype, events.message)
    #  from userinfo, events
    #  where userinfo.riderid == $riderid and events.riderid == $riderid and events.eventid == $eventid
    # (...or, y'know, don't use relational DBs)

    eventrec = SPOTMessageRecord.get(eventid)

    username = eventrec.spotuser.userDispName
    timestamp = eventrec.timestamp
    location = eventrec.location
    msgtype = eventrec.messageType
    message = eventrec.messageDetail
    return render.infowindow(username, timestamp, location, msgtype, message)

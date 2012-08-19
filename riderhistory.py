#!/usr/bin/env python

import web
import json
import time
from cgi import escape

import logging

from datamodels import SPOTMessageRecord, SPOTUser

from google.appengine.ext import db

urls = (
  '/riderhistory/(.*)/', 'riderhistory'
)

riderhistory_app = web.application(urls, locals()).wsgifunc()

class riderhistory:
  def GET(self, riderid):
    forminput = web.input(limit = 250, tstamp = "0")
    historyResults = []

    userrec = db.Query(SPOTUser).filter('userDispName =', riderid).get()
    if userrec is None:
        return json.dumps({'error':"riderid %s not found" % escape(riderid)})
    query = userrec.spotmessages.order('-timeInGMTSecond')

    if forminput.tstamp != "0":
        query = query.filter('timeInGMTSecond >', forminput.tstamp)

    for record in query.run(limit=forminput.limit):
        historyResults.append( record.getSerializeable() )

    web.header('Content-Type', 'application/json')
    return json.dumps(historyResults)

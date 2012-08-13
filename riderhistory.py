#!/usr/bin/env python

import web
import json
import time

urls = (
  '/riderhistory/(.*)', 'riderhistory'
)

riderhistory_app = web.application(urls, locals()).wsgifunc()

class riderhistory:
  def GET(self, riderid):
    forminput = web.input(limit = 250, tstamp = "0")
    #newerthan = web.input(tstamp = int(time.gmtime())+1) # default to everything
    if forminput.tstamp != "0":
        # updated results must ALWAYS be returned as an array, even if there's only one element
    	historyresults = [{'lat': 35.942, 'type': 'TRACK', 'lon': -117.97611, 'id': 17, 'timestamp': '1325376000'},]
    else:
    #select (stampid, lat, lon, type) from historytable where rider = $riderid limit $limit sort by stampid desc
	    historyresults = ({'lat': 35.842, 'type': 'TRACK', 'lon': -117.87611, 'id': 16, 'timestamp': '1325376000'}, {'lat': 35.70541, 'type': 'TRACK', 'lon': -117.86777, 'id': 15, 'timestamp': '1325376000'}, {'lat': 35.58154, 'type': 'TRACK', 'lon': -117.74011, 'id': 14, 'timestamp': '1325376000'}, {'lat': 35.44553, 'type': 'TRACK', 'lon': -117.66187, 'id': 13, 'timestamp': '1325376000'}, {'lat': 35.32247, 'type': 'TRACK', 'lon': -117.61034, 'id': 12, 'timestamp': '1325376000'}, {'lat': 35.16206, 'type': 'TRACK', 'lon': -117.58893, 'id': 11, 'timestamp': '1325376000'}, {'lat': 34.99798, 'type': 'TRACK', 'lon': -117.54318, 'id': 10, 'timestamp': '1325376000'}, {'lat': 34.85088, 'type': 'TRACK', 'lon': -117.50237, 'id': 9, 'timestamp': '1325376000'}, {'lat': 34.69288, 'type': 'TRACK', 'lon': -117.45087, 'id': 8, 'timestamp': '1325376000'}, {'lat': 34.57965, 'type': 'TRACK', 'lon': -117.41273, 'id': 7, 'timestamp': '1325376000'}, {'lat': 34.53742, 'type': 'TRACK', 'lon': -117.39941, 'id': 6, 'timestamp': '1325376000'}, {'lat': 34.43756, 'type': 'TRACK', 'lon': -117.39954, 'id': 5, 'timestamp': '1325376000'}, {'lat': 34.31452, 'type': 'TRACK', 'lon': -117.4778, 'id': 4, 'timestamp': '1325376000'}, {'lat': 34.19201, 'type': 'TRACK', 'lon': -117.36261, 'id': 3, 'timestamp': '1325376000'}, {'lat': 33.10396, 'type': 'TRACK', 'lon': -117.21762, 'id': 2, 'timestamp': '1325376000'}, {'lat': 33.10391, 'type': 'TRACK', 'lon': -117.21759, 'id': 1, 'timestamp': '1325376000'}, {'lat': 33.10391, 'type': 'START', 'lon': -117.21759, 'id': 0, 'timestamp': '1325376000'})
    web.header('Content-Type', 'application/json')
    return json.dumps(historyresults)

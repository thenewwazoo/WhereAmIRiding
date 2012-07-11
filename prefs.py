#!/usr/bin/env python

import web
import json

urls = (
  '/(.*)', 'prefs'
)

class prefs:
  def GET(self, username):
    #prefsdict = {
    #  'disableDefaultUI': True,
    #  'streetViewControl': True,
    #  'panControl': True,
    #  'mapTypeControl': True,
    #  'mapTypeControlOptions': {
    #    'style': 'google.maps.MapTypeControlStyle.HORIZONTAL_BAR',
    #    'position': 'google.maps.ControlPosition.TOP_RIGHT'
    #  },
    #  'zoomControl': True,
    #  'zoomControlOptions': {
    #     'style': 'google.maps.ZoomControlStyle.LARGE'
    #  },
    #  'mapTypeID': 'google.maps.MapTypeId.TERRAIN'
    #}
    prefsdict = {
      'disable_std_ui': True,
      'gmaps_controls': True,
      
    }
    web.header('Content-Type', 'application/json')
    return json.dumps(prefsdict)

prefs_app = web.application(urls, locals())

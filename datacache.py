# coding: utf-8

import web
import logging

from SPOTtransport import SPOTXMLDataGetter
from datamodels import SPOTMessageRecord, SPOTUser

from google.appengine.api import taskqueue
from google.appengine.ext import db

cacheupdate_app = web.application( ('/cache/update', 'CacheUpdateHandler'), locals() ).wsgifunc()
cacheworker_app = web.application( ('/cache/worker', 'CacheWorker'), locals() ).wsgifunc()

class CacheUpdateHandler:
	from google.appengine.api import taskqueue
	def GET(self):
		for user in SPOTUser.all().run():
			mostRecent = user.spotmessages.order('-timeInGMTSecond').get()

			try:
				messageHistory = SPOTXMLDataGetter( user.glId )
			except ValueError as e: # glId invalid or not found
				logging.error( "SPOTXMLDataGetter(%s) error: %r" % (user.glId, str(e)) )
				continue
			except:
				logging.error("unknown error building SPOTXMLDataGetter for %s" % user.glId)
				raise

			for messageElement in messageHistory:
				messageData = SPOTMessageRecord.dictFromMessageTag(messageElement, user.key())
				if not mostRecent or messageData['timeInGMTSecond'] > mostRecent.timeInGMTSecond:
					taskqueue.add(url='/cache/worker', params=messageData)
				else:
					break

		return

class CacheWorker:
	from google.appengine.ext import db
	def POST(self):
		def transact():
			recordDict = SPOTMessageRecord.fixFormTypes(web.input())
			SPOTMessageRecord(**recordDict).put()
		db.run_in_transaction(transact)
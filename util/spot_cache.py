# coding: utf-8

from xml.etree import ElementTree
import urllib, urlparse

#from datamodels import SPOTMessageRecord, SPOTUserRecord

#testglId = "0NNZQDvsWpjOJSeaKYzLhfix1GIAq89Ne"

# get list of users
# for each user in list
#  get their messages xml
#  grab the newest message in the datastore
#  for each xml.message
#   if the xml.message is newer than the datastore.message
#    store the xml.message
#   else break

class SPOTDataGetter(object):
	def __init__(self, glId):
		self.glId = glId
		self.xmldata = self.__getSPOTData(self.glId)
		self.totalCount = self.__getTotalCount(self.xmldata)
		self.knownMessages = self.__getKnownCount(self.xmldata)
		self.currentMessageIdx = 0
		self.currentPage = 1
		self.msgsPerPage = 50

	def __iter__(self):
		return self

	def next(self):
		if self.currentMessageIdx >= self.totalCount:
			raise StopIteration
		else:
			if self.currentMessageIdx >= self.knownMessages:
				self.__getMoreSPOTData()
			currmsg = self.xmldata.findall("message")[self.currentMessageIdx]
			self.currentMessageIdx += 1
			return SPOTMessageRecord.fromMessageTag(currmsg)

	def __buildSPOTUrlArgs(self, glId, complete=False, pagestart=None):
		userarg = "glId"
		completearg = "completeXml" # ["true" | "false"] # we shouldn't need to use this
		paginatearg = "start" # x = 1, 51, 101 – increments of 50

		argtuples = [ (userarg, glId) ]
		if complete is True:
			argtuples.append( (completearg, complete) )
		if pagestart is not None:
			argtuples.append( (paginatearg, pagestart * self.msgsPerPage) )

		return urllib.urlencode( argtuples )

	def __getSPOTData(self, glId, complete=False, pagestart=None):
		dataurl = "http://share.findmespot.com/messageService/guestlinkservlet?%s"
		
		url = dataurl % self.__buildSPOTUrlArgs(glId, complete, pagestart)
		xmldata = ElementTree.parse( urllib.urlopen(url))
		
		return xmldata

	def __getMoreSPOTData(self):
		try:
			newdata = self.__getSPOTData(self.glId, pagestart=self.currentPage)
		except:
			raise

		shift = self.__getTotalCount(newdata) - self.totalCount
		# if shift is >0, a new message has arrived since we got our first page, and all our results
		#  are "shifted" down. This is to prevent duplicate messages.
		for newmsg in newdata.findall("message")[shift:]:
			self.xmldata.getroot().append(newmsg) 

		self.currentPage += 1
		self.knownMessages = self.__getKnownCount(self.xmldata)

	def __getTotalCount(self, xmldata):
		return int( xmldata.getroot().find("totalCount").text) # what has SPOT told us is the max number we can expect?

	def __getKnownCount(self, xmldata):
		return len( xmldata.getroot().findall("message") ) # how many <message> tags are in the xml?

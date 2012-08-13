# coding: utf-8
import urllib
from xml.etree import ElementTree

#testglId = "0NNZQDvsWpjOJSeaKYzLhfix1GIAq89Ne"

class SPOTXMLDataGetter(object):
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
			return currmsg

	def __repr__(self):
		return "<%(classname)s object for %(glId)s [storing %(known)d of %(total)d]>" % {
			'classname': type(self).__name__,
			'glId': self.glId,
			'known': self.knownMessages,
			'total': self.totalCount
		}

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
		xmldata = ElementTree.parse( urllib.urlopen(url) )
		
		try:
			self.__checkErrors(xmldata)
		except:
			raise

		return xmldata

	def __checkErrors(self, xmldata):
		err = xmldata.getroot()
		if err.tag == u"error":
			if err.text == u"Missing guestLinkId" or err.text == u"Wrong guestLinkId":
				raise ValueError(err.text)
			else:
				raise Exception()

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

	def __getTotalCount(self, xmldata):  # what has SPOT told us is the max number we can expect?
		try:
			count = int( xmldata.getroot().find("totalCount").text)
		except:
			count = 0
		return count

	def __getKnownCount(self, xmldata):
		return len( xmldata.getroot().findall("message") ) # how many <message> tags are in the xml?

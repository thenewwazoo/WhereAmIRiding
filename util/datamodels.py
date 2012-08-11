
from google.appengine.ext import db
import iso8601
from pytz import timezone
from datetime import datetime
from time import time

class SPOTUserRecord(db.model):
	user = db.UserProperty()
	glId = db.StringProperty(required=True) # may be empty string in future for non-SPOT expansion
	userURL = db.StringProperty()
	# NOTE: implied property here of SPOTMessageRecord

# model based on XML schema at http://faq.findmespot.com/index.php?action=showEntry&data=69
# see also included file spot_schema.xsd
class SPOTMessageRecord(db.model):
	spotuser = db.ReferenceProperty(SPOTUserRecord, collection_name='spotmessages')

	esn = db.StringProperty(required=True)
	esnName = db.StringProperty()
	messageType = db.StringProperty(required=True, choices=["TEST", "TRACK", "HELP", "SOS"])
	messageDetail = db.StringProperty()
	timestamp = db.DateTimeProperty(required=True) # XML is an ISO8601 timestamp string
	timeInGMTSecond = db.IntegerProperty()
	location = db.GeoPtProperty() # combination of two float values
	nearestTown = db.StringProperty()
	nearestTownDistance = db.StringProperty()

	@classmethod
	def fromMessageTag(recordClass, msgElement):
		"""
		Generate a SPOTMessageRecord object from an XML element

		msgElement: an xml.etree.Element object of type Message. see spot_schema.xsd for details.

		"""
		utc_tz = timezone('UTC')
		gmt_tz = timezone('GMT')
		utc_dt = iso8601.parse_date(msgElement.find('timestamp').text, gmt_tz).astimezone(utc_tz)
		utc_tsec = int( utcdatetime_to_ts(utc_dt) )

		record = recordClass(
			esn = msgElement.find('esn').text,
			messageType = msgElement.find('messageType').text,
			timestamp = utc_dt
			)
		for optionalData in ["esnName", "messageDetail"]:
			tag = msgElement.find(optionalData)
			if tag is not None:
				setattr(record, optionalData, tag.text)

		epochTag = msgElement.find('timeInGMTSecond')
		if epochTag is not None: # we prefer what SPOT gives us
			record.timeInGMTSecond = int(epochTag.text)
		else: # but we'll use calculated values if it's convenient
			record.timeInGMTSecond = utc_tsec

		latTag = msgElement.find('latitude')
		lonTag = msgElement.find('longitude')
		if lonTag is not None and latTag is not None:
			record.location = db.GeoPt(float(latTag.text), float(lonTag.text))

		return record

# dealing with time zones in a pain in the dick
def utcdatetime_to_ts(dt):
   return time.mktime(dt.utctimetuple()) - time.timezone

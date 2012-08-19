
from google.appengine.ext import db
import iso8601
from pytz import timezone
from datetime import datetime
from time import time

from web import form

class SPOTUser(db.Model):
	#userid = db.StringProperty(required=True) # this is google.appengine.api.users.get_current_user().user_id()
	# NOTE: using key_name <- userid
	userDispName = db.StringProperty()
	glId = db.StringProperty(required=True) # may be empty string in future for non-SPOT expansion
	userEmail = db.EmailProperty(required=True)
	userWebsite = db.LinkProperty()
	userIM = db.IMProperty()
	# NOTE: Reference to SPOTUser by SPOTMessageRecord

	@staticmethod
	def buildForm():
		return form.Form(
			form.Textbox("userDispName", form.notnull, description="Display name"),
			form.Textbox("glId", form.notnull, description="SPOT key"),
			form.Textbox("userEmail", form.regexp(r".*@.*", "Must be a valid email address"), description="Email address"),
			form.Textbox("userWebsite", description="Website"),
			form.Textbox("userIM", description="IM nickname")
			)

# model based on XML schema at http://faq.findmespot.com/index.php?action=showEntry&data=69
# see also included file spot_schema.xsd
class SPOTMessageRecord(db.Model):
	spotuser = db.ReferenceProperty(SPOTUser, collection_name='spotmessages')

	esn = db.StringProperty(required=True)
	esnName = db.StringProperty()
	messageType = db.StringProperty(required=True, choices=["TEST", "TRACK", "HELP", "SOS"])
	messageDetail = db.StringProperty()
	timestamp = db.DateTimeProperty(required=True) # XML is an ISO8601 timestamp string
	timeInGMTSecond = db.IntegerProperty()
	location = db.GeoPtProperty() # combination of two float values
	nearestTown = db.StringProperty()
	nearestTownDistance = db.StringProperty()

	def getSerializeable(self):
		outdict = db.to_dict(self)
		outdict['latitude'] = outdict['location'].lat
		outdict['longitude'] = outdict['location'].lon
		del outdict['location']
		outdict['spotuser'] = str(outdict['spotuser'])
		outdict['timestamp'] = outdict['timestamp'].strftime("%Y-%m-%dT%H:%M:%S")
		return outdict

	@classmethod
	def fromMessageTag(recordClass, msgElement):
		return recordClass( **dictFromMessageTag(msgElement) )

	@staticmethod
	def dictFromMessageTag(msgElement, userkey=None):
		"""
		Generate a dictionary from an XML element, munging types as needed.

		msgElement: an xml.etree.Element object of type Message. see spot_schema.xsd for details.
		userkey: the key identifying the user who owns this message

		"""

		recordDict = {}
		for datum in msgElement:
			recordDict[datum.tag] = datum.text
		if userkey:
			recordDict['spotuser'] = userkey

		utc_tz = timezone('UTC')
		gmt_tz = timezone('GMT')
		recordDict['timestamp'] = iso8601.parse_date(recordDict['timestamp'], gmt_tz).astimezone(utc_tz) # convert timestamp from GMT to UTC
		#utc_dt = iso8601.parse_date(msgElement.find('timestamp').text, gmt_tz).astimezone(utc_tz)
		if 'timeInGMTSecond' not in recordDict:
			recordDict['timeInGMTSecond'] = int( utcdatetime_to_ts(utc_dt) )
		else:
			recordDict['timeInGMTSecond'] = int( recordDict['timeInGMTSecond'] )

		try:
			recordDict['location'] = db.GeoPt( float(recordDict['latitude']), float(recordDict['longitude']) )
			del recordDict['latitude']
			del recordDict['longitude']
		except:
			pass

		return recordDict

	@staticmethod
	def fixFormTypes(inputDict):
		"""
		A dirty little helper method to turn the unicode strings that come from forms into other types
		as necessary."""
		inputDict['timeInGMTSecond'] = int(inputDict['timeInGMTSecond'])
		inputDict['timestamp'] = iso8601.parse_date(inputDict['timestamp'])
		inputDict['spotuser'] = db.Key(encoded=inputDict['spotuser'])
		return inputDict

# dealing with time zones in a pain in the dick
def utcdatetime_to_ts(dt):
   return time.mktime(dt.utctimetuple()) - time.timezone

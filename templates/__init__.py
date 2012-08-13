from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def infowindow (username, eventid, time, date, lat, lng, msgtype, message):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'\n'])
    extend_([u'<div id="content"><div id="siteNotice"></div><hr><table cellspacing="1" cellpadding="1" border="0" width="280">\n'])
    extend_([u'<tr><td align="right"><strong>User:</strong></td><td align="center"><strong>', escape_(username, True), u'</strong></td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Point:</strong></td><td align="center">#', escape_(eventid, True), u'</td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Time:</strong></td><td align="center">', escape_(time, True), u'</td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Date:</strong></td><td align="center">', escape_(date, True), u'</td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Lat/Lng:</strong></td><td align="center"><a href="http://maps.google.com/maps?q=', escape_(lat, True), u',', escape_(lng, True), u'" target="_blank">', escape_(lat, True), u', ', escape_(lng, True), u'</a></td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Type:</strong></td><td align="center">', escape_(msgtype, True), u'</td></tr>\n'])
    extend_([u'<tr><td align="right"><strong>Message:</strong></td><td align="center">', escape_(message, True), u'</td></tr></tr></table><hr></p>\n'])

    return self

infowindow = CompiledTemplate(infowindow, 'templates/infowindow.html')
join_ = infowindow._join; escape_ = infowindow._escape

# coding: utf-8
def registration (email, form, logout):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'\n'])
    extend_([u'<p>Hello, ', escape_(email, True), u'!</p>\n'])
    extend_([u'<form name="main" method="post"> \n'])
    if not form.valid:
        extend_([u'<p class="error">Please enter your registration information:</p>\n'])
    extend_([u'<input type=hidden name=csrf_token value="', escape_(csrf_token(), True), u'">\n'])
    extend_([escape_(form.render(), False), u'\n'])
    extend_([u'<input type="submit" />\n'])
    extend_([u'</form>\n'])
    extend_([u'<p><a href="', escape_(logout, True), u'">Log out</a></p>\n'])

    return self

registration = CompiledTemplate(registration, 'templates/registration.html')
join_ = registration._join; escape_ = registration._escape

# coding: utf-8
def usermap (ridername, riderid, riderurl, riderglId):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'\n'])
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html>\n'])
    extend_([u'<head>\n'])
    extend_([u'\n'])
    extend_([u'<link rel="stylesheet" type="text/css" href="/static/css/default.css" />\n'])
    extend_([u'<link rel="stylesheet" type="text/css" href="/static/css/style.css" />\n'])
    extend_([u'\n'])
    extend_([u'<title>Trip Tracker - ', escape_(ridername, True), u'</title>\n'])
    extend_([u'\n'])
    extend_([u'<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?libraries=weather&sensor=false"></script>\n'])
    extend_([u'<!-- <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAE46eJan0szd83J6Fa9e3tlo043KHXB00&libraries=weather&sensor=false"></script> -->\n'])
    extend_([u'<script type="text/javascript" src="http://code.jquery.com/jquery-1.7.2.js"></script>\n'])
    extend_([u'\n'])
    extend_([u'<script type="text/javascript">\n'])
    extend_([u'var riderid = "', escape_(riderid, True), u'";\n'])
    extend_([u'</script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/riderhistory.js"></script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/maplayerctl.js"></script>\n'])
    extend_([u'\n'])
    extend_([u'</head>\n'])
    extend_([u'\n'])
    extend_([u'  <body onload="initialize()">\n'])
    extend_([u'  <div id="map_canvas"></div>\n'])
    extend_([u'\n'])
    extend_([u'        <div class="mapinfo">\n'])
    extend_([u'        <strong>Map Options:</strong><br />\n'])
    extend_([u'        <select name="map_type" onChange="updateMapType(this, map);">\n'])
    extend_([u'          <option value="ROADMAP"  />Roads</option>\n'])
    extend_([u'          <option value="TERRAIN" selected="selected" />Terrain</option>\n'])
    extend_([u'          <option value="SATELLITE"  />Satellite</option>\n'])
    extend_([u'        </select><br />\n'])
    extend_([u'          <input type="checkbox" name="weather" value="ON" onClick="toggleLayer(weatherLayer, map);" /> Weather<br />\n'])
    extend_([u'          <input type="checkbox" name="clouds" value="ON"  onClick="toggleLayer(cloudLayer, map);" /> Clouds<br />\n'])
    extend_([u'          <input type="checkbox" name="traffic" value="ON"  onClick="toggleLayer(trafficLayer, map);" /> Traffic<br />\n'])
    extend_([u'          <input type="checkbox" name="fulltrip" value="ON" onClick="toggleZoom();" /> Full Trip<br />\n'])
    extend_([u'    <hr />\n'])
    extend_([u"        <font color='grey'><strong>Premium:</strong></font><br />\n"])
    extend_([u"          <font color='grey'>Auto-Refresh:</font> <font color='red'>OFF</font><br />\n"])
    extend_([u'          <input type="checkbox" name="highlight" value="ON" unchecked disabled /> <font color=\'grey\'> Highlight:</font> <font color=\'red\'>OFF</font><br />\n'])
    extend_([u'          <input type="checkbox" name="images" value="OFF" unchecked disabled /> <font color=\'grey\'> Hide Images</font><br />\n'])
    extend_([u'          <input type="checkbox" name="controls" value="OFF" unchecked disabled /> <font color=\'grey\'> Hide Controls</font><br />\n'])
    extend_([u'          <input type="checkbox" name="options" value="OFF"  disabled /> <font color=\'grey\'> Hide Options</font><br />\n'])
    extend_([u'          <input type="checkbox" name="overlays" value="OFF" unchecked disabled /> <font color=\'grey\'> Hide Overlays</font><br />\n'])
    extend_([u'        </div>\n'])
    extend_([u'\n'])
    extend_([u'        <div id="footer_url">\n'])
    extend_([u"          <a href='http://www.whereamiriding.com' target='_parent'>&copy; 2012 - WhereAmIRiding.com</a>\n"])
    extend_([u'        </div>\n'])
    extend_([u'\n'])
    extend_([u'        <div id="footer_spot_logo">\n'])
    extend_([u"          <a href='http://share.findmespot.com/shared/faces/viewspots.jsp?glId=", escape_(riderglId, True), u"' target='_blank'><img src='/static/images/spotlogo02.png' title='Click to see this user on FindMeSpot.com' alt='Click to see this user on FindMeSpot.com' width='48' ></a>\n"])
    extend_([u'        </div>\n'])
    extend_([u'\n'])
    extend_([u'        <div id="images">\n'])
    extend_([u"          <a href='", escape_(riderurl, True), u"' title='", escape_(ridername, True), u"' alt='", escape_(ridername, True), u"' target='_blank'>\n"])
    extend_([u"      <img src='/static/images/users/", escape_((riderid), True), u'.png\' width=\'100\' onerror="this.src=\'/static/images/logo-icon2.png\';">\n'])
    extend_([u'    </a>\n'])
    extend_([u'        </div>\n'])
    extend_([u'\n'])
    extend_([u'  </body>\n'])
    extend_([u'</html>\n'])

    return self

usermap = CompiledTemplate(usermap, 'templates/usermap.html')
join_ = usermap._join; escape_ = usermap._escape

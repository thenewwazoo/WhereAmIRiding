// variable riderid is defined in the HTML, as
// var riderid = "username"

var controlsOptions = {};
var infowindow = new google.maps.InfoWindow();
var map;

var lastUpdate = Math.round(Date.now() / 1000);

var defaultZoom = 17;
var isFullZoom = false;

var markerImages = {
  START: 'http://www.whereamiriding.com/gpsfiles/map/images/start.png',
  TRACK: 'http://www.whereamiriding.com/gpsfiles/map/images/marker-green-mini.png',
  TEST:  'http://www.whereamiriding.com/gpsfiles/map/images/plus.png',
  HELP:  'http://www.whereamiriding.com/gpsfiles/map/images/minus.png',
  END:   'http://www.whereamiriding.com/gpsfiles/map/images/motorcycle2.png'
}

// this is hacky. fix the preferences model
// seriously. ignore the way this works. it needs a lot of re-thinking
function getControlsOptions(riderid) {
  jQuery.getJSON('/prefs/' + riderid + "/", function(opts) {
    controlsOptions.disableDefaultUI = opts.disable_std_ui;
    controlsOptions.streetViewControl = opts.gmaps_controls;
    controlsOptions.panControl = opts.gmaps_controls;
    controlsOptions.mapTypeControl = opts.gmaps_controls;
    controlsOptions.mapTypeControlOptions = { style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR, position: google.maps.ControlPosition.TOP_RIGHT };
    controlsOptions.zoomControl = opts.gmaps_controls;
    controlsOptions.zoomControlOptions = { style: google.maps.ZoomControlStyle.LARGE };
    controlsOptions.mapTypeId = google.maps.MapTypeId.TERRAIN;

    map.setOptions(controlsOptions)

  });
};

function updateHistoryMap() {
  console.log("updating map since " + lastUpdate);
  getHistoryData(riderid, true);
  lastUpdate = Math.round(Date.now() / 1000);
}

function updateRiderMap() {
  console.log("updating map since " + lastUpdate);
  getRiderPositions(true);
  lastUpdate = Math.round(Date.now() / 1000);
}

var historyData = new function () {
  this.historyArray = new Array();
  this.ridePath = new google.maps.Polyline({
        strokeColor: "#0000c8",
        strokeOpacity: 2,
        strokeWeight: 2
        });

  this.addEntry = function(newEvent) {
    // keep historyArray ordered
    if (this.historyArray.length == 0 || this.historyArray[0].timestamp > newEvent.timestamp) {
      this.historyArray.splice(0, 0, newEvent);
      this.getRidePath().getPath().insertAt(0, newEvent.position);
      return 0;
    }
    for (var i = this.historyArray.length - 1; i >= 0; --i) {
      var event = this.historyArray[i];
      if (event.timestamp < newEvent.timestamp) {
        this.historyArray.splice(i + 1, 0, newEvent);
        this.getRidePath().getPath().insertAt(i + 1, newEvent.position);
      }
    }
  };

  this.clearHistory = function() {
    for (var i = 0; i < this.historyArray.length; i++) {
      this.historyArray[i].setMap(null);
      delete this.historyArray[i];
    }
    this.ridePath.setMap(null);
    this.ridePath = new google.maps.Polyline({
      strokeColor: "#0000c8",
      strokeOpacity: 2,
      strokeWeight: 2
      });
  };

  this.length = function() {}

  this.getEventAt = function(index) {
    return this.historyArray[index];
  };

  this.getLastEvent = function() {
    return this.historyArray[this.historyArray.length - 1];
  };

  this.getRidePath = function() {
    return this.ridePath;
  }

}

function SPOTMessageRecord(jsonDatum) {
  // constructor section
  this.esn = jsonDatum['esn'];
  this.messageType = jsonDatum['messageType'];
  this.timestamp = new Date(jsonDatum['timestamp']);
  this.key = jsonDatum['key'];
  this.spotuserkey = jsonDatum['spotuser'];

  if ('esnName' in jsonDatum) { this.esnName = jsonDatum['esnName']; }
  if ('messageDetail' in jsonDatum) { this.messageDetail = jsonDatum['messageDetail']; }
  // jsonDatum['timestamp'] is an ISO8601 string
  if ('timeInGMTSecond' in jsonDatum) {
    this.timeInGMTSecond = parseInt(jsonDatum['timeInGMTSecond']); 
  } else { 
    /* convert ISO8601 to epoch time */ 
  }
  if ('latitude' in jsonDatum && 'longitude' in jsonDatum) { this.position = new google.maps.LatLng(parseFloat(jsonDatum['latitude']), parseFloat(jsonDatum['longitude'])); }
  if ('nearestTown' in jsonDatum) { this.nearestTown = jsonDatum['nearestTown']; }
  if ('nearestTownDistance' in jsonDatum) { this.nearestTownDistance = parseFloat(jsonDatum['nearestTownDistance']); }
  // end constructor section

  this.getMapPin = function(map) {
    if ('mapPin' in this) {
      return this.mapPin;
    } else {
      this.mapPin = new google.maps.Marker( {
        position: this.position,
        icon: markerImages[this.messageType],
        title: "(" + this.position.toString() + ") @ [" + this.timestamp + "]"
      });
      return this.mapPin;
    }
  };
}

function getHistoryData(riderid, isUpdate) {
  var histURL = "/riderhistory/" + riderid + "/";

  jQuery.getJSON( histURL,
    { tstamp: (isUpdate ? lastUpdate : 0) },
    function (riderHist, textStatus, jqXHR) {

      jQuery.each(riderHist, function(i, entry) {
        var spotmsg = new SPOTMessageRecord(entry);
        var msgpin = spotmsg.getMapPin();
        msgpin.setMap(map);
        google.maps.event.addListener(msgpin, 'click', function() {
          infowindow.close();
          getEventInfo(spotmsg);
        });
        historyData.addEntry(spotmsg);
      });
      zoomMap(defaultZoom);
      updateRiderPosMarker();

    }
  );

}

function getRiderPositions(isUpdate) {
  var posURL = "/riderhistory/";

  if (isUpdate) {
    historyData.clearHistory();
  }

  jQuery.getJSON( posURL,
    { tstamp: (isUpdate ? lastUpdate: 0) },
    function (riderPos, textStatus, jqXHR) {
      shadowImage = new google.maps.MarkerImage( "/static/images/shadow-usericon.png", 
        null, null, new google.maps.Point(11, 25), new google.maps.Size(29, 25) );
      jQuery.each(riderPos, function(i, entry) {
        var spotmsg = new SPOTMessageRecord(entry);
        var msgpin = spotmsg.getMapPin();
        msgpin.setIcon(
          new google.maps.MarkerImage(
            "/userimage/" + entry['spotuser'] + "/", 
            null, null, null, new google.maps.Size(22, 25)
          )
        );
        msgpin.setShadow(shadowImage);
        msgpin.setMap(map);
        google.maps.event.addListener(msgpin, 'click', function() {
          infowindow.close();
          getEventInfo(spotmsg);
        });
        historyData.addEntry(spotmsg);
      });
      zoomMap(); // show everyone on the map at once
    }
  );
}

function updateRiderPosMarker()
{
  jQuery.each(historyData.historyArray, function(i, histEvent){
    if (histEvent.getMapPin().getIcon() == markerImages['END']) {
      histEvent.getMapPin().setIcon(markerImages[histEvent.messageType]);
    }
  });
  if (historyData.getLastEvent().messageType == 'TRACK') {
    historyData.getLastEvent().getMapPin().setIcon(markerImages['END']);
  }
}

function getEventInfo(spotmsg) {
  jQuery.ajax({
    url: "/eventinfo/" + spotmsg.key + "/",
    success: function(data) {
      infowindow.setContent(data);
      infowindow.open(map, spotmsg.getMapPin());
    }
  });
}

function zoomMap(zoomPoints) {
  var bounds = new google.maps.LatLngBounds();
  var pathlen = historyData.getRidePath().getPath().length;

  if (typeof zoomPoints === 'undefined') {
    zoomPoints = historyData.getRidePath().getPath().length;
  }

  if (zoomPoints > pathlen) {
    zoomPoints = pathlen;
  }

  for (var i = zoomPoints; i > 0; --i) {
    bounds.extend( historyData.getEventAt( historyData.historyArray.length - i ).position );
  }

  map.fitBounds(bounds);
}

function toggleZoom() {
  if (isFullZoom) {
    zoomMap(defaultZoom);
    isFullZoom = false;
  } else {
    zoomMap();
    isFullZoom = true;
  }
}

function initialize() {

  var SF = new google.maps.LatLng(37.7793, -122.4192);
  var initialOpts = { center: SF, // this is mandatory, but immediately gets changed
          zoom: 12,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };

  map = new google.maps.Map(document.getElementById("map_canvas"), initialOpts);

  if (riderid != "") {
    getControlsOptions();

    historyData.getRidePath().setMap(map);
    getHistoryData(riderid, false);

    setInterval(updateHistoryMap, 1000 * 60 * 10);    
  }
  else
  {
    getControlsOptions();
    getRiderPositions(false);
    setInterval(updateRiderMap, 1000*60*10);
  }

}

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
function getControlsOptions() {
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

function updateMap() {
  console.log("updating map since " + lastUpdate);
  getHistoryData(true);
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
  if ('esnName' in jsonDatum) { this.esnName = jsonDatum['esnName']; }
  this.messageType = jsonDatum['messageType'];
  if ('messageDetail' in jsonDatum) { this.messageDetail = jsonDatum['messageDetail']; }
  // jsonDatum['timestamp'] is an ISO8601 string
  this.timestamp = new Date(jsonDatum['timestamp']);
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

function getHistoryData(isUpdate) {
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
          getEventInfo(msgpin, spotmsg);
        });
        historyData.addEntry(spotmsg);
      });
      zoomMap(defaultZoom);
      updateRiderPosMarker();

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
  historyData.getLastEvent().getMapPin().setIcon(markerImages['END']);
}

function getEventInfo(marker, riderevent) {
  jQuery.ajax({
    url: "/eventinfo/" + riderid + "/" + riderevent + "/",
    success: function(data) {
      infowindow.setContent(data);
      infowindow.open(map, marker);
    }
  });
}

function zoomMap(zoomPoints) {
  var bounds = new google.maps.LatLngBounds();
  var pathlen = historyData.getRidePath().getPath().length;

  if (typeof zoomPoints === 'undefined') {
    zoomPoints = historyData.getRidePath().getPath().length;
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

  getControlsOptions();

  historyData.getRidePath().setMap(map);
  getHistoryData(false);

  setInterval(updateMap, 1000 * 60 * 10);

}

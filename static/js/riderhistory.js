// variable riderid is defined in the HTML, as
// var riderid = "username"

var controlsOptions = {};
var ridePath;
var infowindow = new google.maps.InfoWindow();
var map;

var riderMarkers = [];
var lastUpdate = Math.round(Date.now() / 1000);

var defaultZoom = 7;
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
  jQuery.getJSON('/prefs/' + riderid, function(opts) {
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
  getHistoryData(lastUpdate);
  lastUpdate = Math.round(Date.now() / 1000);
}

function getRideHistory() {
  getHistoryData(0);
}

function getHistoryData(newerthan) {
  var historyArray = ridePath.getPath();

  var histURL = "/ridehistory/" + riderid + (newerthan > 0 ? "?tstamp="+newerthan : "");
  jQuery.getJSON(histURL, function(hist) {
    jQuery.each( hist, function(i, entry) {
      var eventidx = entry['id'];
      var position = new google.maps.LatLng(entry['lat'], entry['lon']);
      console.log('added hist ' + eventidx + ' @ ' + position);
      historyArray.setAt(eventidx, position);

      var eventtype = entry['type'];
      addMapPin(position, eventtype, eventidx);

    });

    updateRiderPosMarker();
    zoomMap(defaultZoom);

  });
};

function addMapPin(position, eventtype, index) {
  var icon = markerImages[eventtype];
  var title = "[#" + index + "] @ (" + position.toString() + ")";
  var marker = new google.maps.Marker({ position: position, 
                                    map: map, 
                                    icon: icon,
                                    zIndex: 1,
                                    title: title
                                  });
  google.maps.event.addListener(marker, 'click', function () {
    infowindow.close();
    getEventInfo(marker, index);
  });
  riderMarkers[index] = marker;
}

function updateRiderPosMarker()
{
  jQuery.each(riderMarkers, function(i, marker){
    if (marker.getIcon() == markerImages['END']) {
      marker.setIcon(markerImages['TRACK']);
    }
  });
  riderMarkers[riderMarkers.length - 1].icon = markerImages['END'];
}

function getEventInfo(marker, riderevent) {
  jQuery.ajax({
    url: "/eventinfo/" + riderid + "/" + riderevent,
    success: function(data) {
      infowindow.setContent(data);
      infowindow.open(map, marker);
    }
  });
}



function initialize() {
  var SF = new google.maps.LatLng(37.7793, -122.4192);
  var initialOpts = { center: SF, // this is mandatory, but immediately gets changed
          zoom: 12,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };

  map = new google.maps.Map(document.getElementById("map_canvas"), initialOpts);

  getControlsOptions();

  ridePath = new google.maps.Polyline({
        strokeColor: "#0000c8",
        strokeOpacity: 2,
        strokeWeight: 2
        });
  ridePath.setMap(map);

  getRideHistory();

  setInterval(updateMap, 1000 * 60 * 10);

}

function zoomMap(zoomPoints) {
  var bounds = new google.maps.LatLngBounds();
  if (typeof zoomPoints === 'undefined') {
    zoomPoints = ridePath.getPath().length;
  }
  var pathlen = ridePath.getPath().length;

  bounds.extend( ridePath.getPath().getAt( pathlen - 1) );
  bounds.extend( ridePath.getPath().getAt( pathlen - zoomPoints < 0 ? 0 : pathlen - zoomPoints ) );

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
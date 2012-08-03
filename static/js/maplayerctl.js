
var weatherLayer = new google.maps.weather.WeatherLayer({
  temperatureUnits: google.maps.weather.TemperatureUnit.FAHRENHEIT
});
var cloudLayer = new google.maps.weather.CloudLayer();
var trafficLayer = new google.maps.TrafficLayer();

function toggleLayer(layer, map) {
  if (layer.getMap()) {
    layer.setMap(null);
  } else {
    layer.setMap(map);
  }
}

function updateMapType(mapTypeSelector, map) {
  var mapType = mapTypeSelector.options[mapTypeSelector.selectedIndex].value;
  switch (mapType) {
    case "TERRAIN":
      map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
      break;
    case "SATELLITE":
      map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
      break;
    default:
      map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
  }
}
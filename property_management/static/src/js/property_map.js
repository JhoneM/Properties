function initialize() {

    const lat = document.getElementById("coordenada_lat").innerHTML
    const lng = document.getElementById("coordenada_lng").innerHTML

    var mapProp = {
        center: new google.maps.LatLng(lat, lng),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);

    new google.maps.Marker({
        position: new google.maps.LatLng(lat, lng),
        map,
    });
}

google.maps.event.addDomListener(window, 'load', initialize);
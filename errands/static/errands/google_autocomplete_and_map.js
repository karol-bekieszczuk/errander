$.getScript( "https://maps.googleapis.com/maps/api/js?key=" + google_api_key + "&libraries=places")
.done(function( script, textStatus ) {
    google.maps.event.addDomListener(window, "load", initialize)

})
$(document).ready(function () {
    $("#latitudeArea").addClass("d-none");
    $("#longtitudeArea").addClass("d-none");
});


function initialize() {
    var input = document.getElementById('autocomplete');
    var autocomplete = new google.maps.places.Autocomplete(input);

    autocomplete.addListener('place_changed', function () {
        var place = autocomplete.getPlace();
        let lat = place.geometry['location'].lat();
        let lng = place.geometry['location'].lng();
        $('#latitude').val(lat);
        $('#longitude').val(lng);

        $("#latitudeArea").removeClass("d-none");
        $("#longtitudeArea").removeClass("d-none");

        document.getElementById("id_geolocation").value = lat+'|'+lng;
        initMap(lat,lng,input.value);
    });
}

function initMap(lat,lng,address) {
    var location = new google.maps.LatLng(lat,lng);
    var mapOptions = {
      zoom: 15,
      center: location,
    }
    var map = new google.maps.Map(document.getElementById("map"), mapOptions);

    var marker = new google.maps.Marker({
        position: location,
        title:address
    });
    marker.setMap(map);
}
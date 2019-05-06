jQuery(document).ready(function (e) {
    jQuery.ajax({
        method: 'post',
        url: ipAjaxVar.ajaxurl,
        data: {
            action: 'get_markers_xml',
        }
    }).done(function (msg) {
        document.getElementById("map").style.height =   "400px";
        var map = new google.maps.Map(document.getElementById('map'), {
            center: new google.maps.LatLng(-33.863276, 151.207977),
            zoom: 12
        });
        var infoWindow = new google.maps.InfoWindow;
        var xml = (new DOMParser()).parseFromString(msg, "application/xml");
        var markers = xml.documentElement.getElementsByTagName('marker');
        Array.prototype.forEach.call(markers, function (markerElem) {
            var id = markerElem.getAttribute('id');
            var name = markerElem.getAttribute('name');
            var address = markerElem.getAttribute('address');
            var point = new google.maps.LatLng(
                parseFloat(markerElem.getAttribute('lat')),
                parseFloat(markerElem.getAttribute('lng')));

            var infowincontent = document.createElement('div');
            var strong = document.createElement('strong');
            strong.textContent = name
            infowincontent.appendChild(strong);
            infowincontent.appendChild(document.createElement('br'));

            var text = document.createElement('text');
            text.textContent = address
            infowincontent.appendChild(text);
            var marker = new google.maps.Marker({
                map: map,
                position: point
            });
            marker.addListener('click', function () {
                infoWindow.setContent(infowincontent);
                infoWindow.open(map, marker);
            });
        });

    });
});

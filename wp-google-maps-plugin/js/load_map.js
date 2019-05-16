jQuery(document).ready(function (e) {
    var filters;
    var map;
    var markersArray = [];

    jQuery.ajax({
        method: 'post',
        url: ipAjaxVar.ajaxurl,
        data: {
            action: 'post_marker_filters'
        }, error:function(msg) {
            console.log(msg);
        }
    }).done(function(msg) {
        filters = msg.split(',');
    });

    jQuery.ajax({
        method: 'post',
        url: ipAjaxVar.ajaxurl,
        data: {
            action: 'post_markers_xml',
        }
    }).done(function (msg) {
        initFilters(filters);

        map = new google.maps.Map(document.getElementById('map'), {
            center: new google.maps.LatLng(51.507422, -0.127595),
            zoom: 10
        });
        var infoWindow = new google.maps.InfoWindow;
        var xml = (new DOMParser()).parseFromString(msg, "application/xml");
        var markers = xml.documentElement.getElementsByTagName('marker');
	var i = 0;        
	Array.prototype.forEach.call(markers, function (markerElem) {
            var id = markerElem.getAttribute('id');
            var name = markerElem.getAttribute('name');
            var address = markerElem.getAttribute('address');
	    var type = markerElem.getAttribute('type');
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
	    markersArray[i] = [marker, type];
            i++;
            marker.addListener('click', function () {
                infoWindow.setContent(infowincontent);
                infoWindow.open(map, marker);
            });
        });

    });

    function initFilters(filters) {
        var container = document.getElementById("map-filters");
        for(var i = 0;i < filters.length - 1;i++) {
            var input = document.createElement("input");
            input.setAttribute("type", "checkbox");
            input.setAttribute("name", filters[i]);
            input.onclick = (function(filter){
                return function(){
                    updateMarkers(filter);
                }
            })(filters[i]);
            input.value = filters[i];
            input.id = filters[i];
            input.checked = true;
            container.appendChild(input);
            var label = document.createElement("label");
            label.setAttribute("for", filters[i]);
            label.innerHTML = filters[i] + "<br>";
            container.appendChild(label);
        }
    }

    function updateMarkers(filter) {
        var newMap = document.getElementById(filter).checked ? map : null;

        for(var i = 0;i < markersArray.length;i++){
            if(markersArray[i][1] == filter) {
                markersArray[i][0].setMap(newMap);
            }
        }
    }
});

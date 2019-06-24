jQuery(document).ready(function (e) {
    var filters;
    var active_filters = [];
    var map;
    var markersArray = [];

    jQuery.ajax({
        method: 'post',
        url: ipAjaxVar.ajaxurl,
        data: {
            action: 'post_marker_filters'
        }, error: function (msg) {
            console.log(msg);
        }
    }).done(function (msg) {
        filters = msg.split(',');
        initFilters(filters);

        map = new google.maps.Map(document.getElementById('map'), {
            center: new google.maps.LatLng(51.507422, -0.127595),
            zoom: 10
        });
    });

    function get_markers(filter) {
        jQuery.ajax({
            method: 'post',
            url: ipAjaxVar.ajaxurl,
            data: {
                action: 'post_marker_xml',
                filter: filter,
            }, error: function (msg) {
                console.log(msg);
            }
        }).done(function (msg) {
            var infoWindow = new google.maps.InfoWindow;
            var xml = (new DOMParser()).parseFromString(msg, "application/xml");
            var markers = xml.documentElement.getElementsByTagName('marker');
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
                infowincontent.appendChild(document.createElement('br'));

                var type_text = document.createElement('text');
                type_text.textContent = type;
                infowincontent.appendChild(type_text);

                var marker = new google.maps.Marker({
                    map: map,
                    position: point
                });
                markersArray.push([marker, type]);
                marker.addListener('click', function () {
                    infoWindow.setContent(infowincontent);
                    infoWindow.open(map, marker);
                });
            });
            document.getElementById("marker-number").textContent = markersArray.length;
        });
    }

    function initFilters(filters) {
        var container = document.getElementById("map-filters");
        if (container == null) {
            container = document.createElement("div");
            container.id = "map-filters-fs";
            document.body.appendChild(container);

            var input_container = document.createElement("div");
            input_container.id = "input_container";
            container.appendChild(input_container);

            var applied_filters = document.createElement("div");
            applied_filters.id = "filters-list";
            var filter_input = document.createElement("input");
            filter_input.type = "text";
            filter_input.id = "filter-input";
            filter_input.placeholder = "Type filter here..."
            filter_input.onkeydown = function (event) {
                if (event.which == 13) {
                    apply_filter(filter_input.value);
                    filter_input.value = "";
                }
            };
            autocomplete(filter_input, filters);
            input_container.appendChild(filter_input);
            var apply_button = document.createElement("button");
            apply_button.id = "apply-button";
            apply_button.textContent = "Apply";
            apply_button.onclick = function (event) {
                apply_filter(document.getElementById("filter-input").value);
                filter_input.value = "";
            }
            input_container.appendChild(apply_button);
            container.appendChild(applied_filters);


            var latLngFields = [];
            var filter_area_button = document.createElement("button");
            for(var i = 0; i < 4;i++) {
                latLngFields[i] = document.createElement("input");
                latLngFields[i].type = "text";
                container.appendChild(latLngFields[i]);
            }
            filter_area_button.id = "filter-area";
            filter_area_button.textContent = "Filter area"
            filter_area_button.onclick = function () {
                console.log(Number(latLngFields[0].value));
                filter_area(new google.maps.LatLngBounds(
                    new google.maps.LatLng(Number(latLngFields[0].value), Number(latLngFields[1].value)),
                    new google.maps.LatLng(Number(latLngFields[2].value), Number(latLngFields[3].value)),
                ));
            }
            container.appendChild(filter_area_button);

            var marker_counter = document.createElement("div");
            marker_counter.id = "marker-counter";
            var marker_number = document.createElement("span");
            marker_number.id = "marker-number";
            marker_number.textContent = 0;
            marker_counter.textContent = "current markers: ";
            container.appendChild(marker_counter);
            marker_counter.appendChild(marker_number);
        }
    }

    function filter_area(bbox) {
        for (var i = markersArray.length - 1; i >= 0; i--) {
            if (!bbox.contains(markersArray[i][0].position)) {
                markersArray[i][0].setMap(null);
                markersArray.splice(i, 1);
            }
        }
        document.getElementById("marker-number").textContent = markersArray.length;
    }

    function removeMarkers(filter) {
        for (var i = markersArray.length - 1; i >= 0; i--) {
            if (markersArray[i][1] == filter) {
                markersArray[i][0].setMap(null);
                markersArray.splice(i, 1);
            }
        }
        document.getElementById("marker-number").textContent = markersArray.length;
    }

    function apply_filter(filter) {
        if (filters.includes(filter) && !active_filters.includes(filter)) {
            get_markers(filter);

            var new_filter = document.createElement("div");
            new_filter.className = "applied-filter";
            new_filter.textContent = filter;
            var close_button = document.createElement("span");
            close_button.textContent = " x";
            close_button.className = "close-filter";
            close_button.onclick = (function (filter, divElem) {
                return function () {
                    removeMarkers(filter);
                    divElem.parentNode.removeChild(divElem);

                    for(var i = 0;i < active_filters.length;i++) {
                        if(active_filters[i] == filter) {
                            active_filters.splice(i, 1);
                            break;
                        }
                    }
                }

            })(filter, new_filter);

            document.getElementById("filters-list").appendChild(new_filter);
            new_filter.appendChild(close_button);

            active_filters.push(filter);
        }
    }
});

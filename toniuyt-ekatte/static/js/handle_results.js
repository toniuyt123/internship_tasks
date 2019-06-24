$(document).ready(function() {
    $("#search").on('click', function() {
        $.ajax( {
            type: "POST",
            url: "/search",
            contentType: "application/json",
            data: JSON.stringify({query: $("#query").val()}),
            dataType: "json",
            success: function(response) {
                container = document.getElementById('container');
                while(container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                document.getElementById("count").textContent = response.length;
                keys = Object.keys(response[0]);

                key_header = document.createElement('thead');
                key_header.appendChild(document.createElement("tr"));
                for(var i = 0;i < keys.length;i++) {
                    elem = document.createElement('th');
                    key = keys[i];
                    elem.textContent = key;
                    key_header.firstChild.appendChild(elem);
                }
                container.appendChild(key_header);

                tbody = document.createElement('tbody');
                container.appendChild(tbody);
                for(var i = 0;i < response.length;i++) {
                    entry = response[i];
                    entry_container = document.createElement('tr');
                    entry_container.classList.add("entry-container");
                    for(var j = 0;j < keys.length;j++) {
                        elem = document.createElement('td');
                        key = keys[j];
                        elem.textContent = entry[key];
                        elem.classList.add(key.replace(" ", "-"));
                        entry_container.appendChild(elem);
                    }
                    tbody.appendChild(entry_container);
                }
            },
            error: function(err) {
                console.log(err);
            }
        });
    });
});
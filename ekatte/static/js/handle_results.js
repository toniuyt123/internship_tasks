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

                key_header = document.createElement('tr');
                for(var i = 0;i < Object.keys(response[0]).length;i++) {
                    elem = document.createElement('th');
                    key = Object.keys(response[0])[i];
                    elem.textContent = key;
                    elem.classList.add("entry-info");
                    key_header.appendChild(elem);
                }
                container.appendChild(key_header);

                for(var i = 0;i < response.length;i++) {
                    entry = response[i];
                    entry_container = document.createElement('tr');
                    entry_container.classList.add("entry-container");
                    for(var j = 0;j < Object.keys(entry).length;j++) {
                        elem = document.createElement('td');
                        key = Object.keys(entry)[j];
                        elem.textContent = entry[key];
                        elem.classList.add(key);
                        elem.classList.add('entry-info');
                        entry_container.appendChild(elem);
                    }
                    container.appendChild(entry_container);
                }
            },
            error: function(err) {
                console.log(err);
            }
        });
    });
});
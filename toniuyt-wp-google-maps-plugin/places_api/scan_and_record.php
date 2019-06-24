<?php
require("dbinfo.php");
require("api_key.php");

$connection = mysqli_connect('localhost', $username, $password);
if (!$connection) {
    die('Not connected : ' . mysqli_error($connection));
}

// Set the active MySQL database
$db_selected = mysqli_select_db($connection, $database);
if (!$db_selected) {
    die('Can\'t use db : ' . mysqli_error($connection));
}

$start_coord = array(-0.292904, 51.425181);
$end_coord = array(0.073584, 51.621142);
$step = 0.008;
$ch = curl_init();
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$count = 0;
for ($x = $start_coord[0]; $x < $end_coord[0]; $x += $step) {
    for ($y = $start_coord[1]; $y < $end_coord[1]; $y += $step) {
        $other_x = $x + $step;
        $other_y = $y + $step;
        $bbox = "$x,$y,$other_x,$other_y";
        //construct and sent curl
        curl_setopt($ch, CURLOPT_URL, "https://places.cit.api.here.com/places/v1/discover/search?app_code=$app_code&app_id=$app_id&q=store&in=$bbox");

        //record to database
        $server_output = curl_exec($ch);
        $obj = json_decode($server_output);
        $count += count($obj->results->items);
        echo $count;
        echo "\n";
        foreach ($obj->results->items as $item) {
            $title = mysqli_real_escape_string($connection, $item->title);
            $address = mysqli_real_escape_string($connection, $item->vicinity);
            $lat = $item->position[0];
            $lng = $item->position[1];
            $type = $item->category->id;
            $query = "INSERT INTO markers(name, address, lat, lng, type) VALUES ('" . $title . "', '" . $address . "', '" . $lat . "', '" . $lng . "', '" . $type . "')";
            $result = mysqli_query($connection, $query);
            if (!$result) {
                die('Invalid query: ' . mysqli_error($connection));
            }
        }
    }
}
curl_close($ch);

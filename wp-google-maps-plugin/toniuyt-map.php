<?php
/**
 * @package Toniuyt
 */
/*
Plugin Name: Simple Google Map
Plugin URI: https://www.google.com
Description: My first plugin.
Version: 1.0.0
Author: Antonio Milev
Author URI: https://www.google.com
License: GPLv2 or later
Text Domain: toniuyt-map
*/
add_shortcode('google-map', 'add_map');

function add_map(){
    wp_enqueue_script('load_map', plugins_url('/js/load_map.js', __FILE__), array('jquery'), '', true);

    wp_localize_script('load_map', 'ipAjaxVar', array(
        'ajaxurl' => admin_url('admin-ajax.php')
    ));

    echo "<div id=\"map\"></div>
    <script async defer src=\"https://maps.googleapis.com/maps/api/js?key=API_KEY&callback=initMap\"> </script>";
}

add_action('wp_ajax_get_markers_xml', 'get_markers_xml');
function get_markers_xml() {
    require("dbinfo.php");

    $dom = new DOMDocument("1.0");
    $node = $dom->createElement("markers");
    $parnode = $dom->appendChild($node);

    // Opens a connection to a MySQL server
    $connection=mysqli_connect ('localhost', $username, $password);
    if (!$connection) {
    die('Not connected : ' . mysqli_error($connection));
    }

    // Set the active MySQL database
    $db_selected = mysqli_select_db($connection, $database);
    if (!$db_selected) {
    die ('Can\'t use db : ' . mysqli_error($connection));
    }

    // Select all the rows in the markers table
    $query = "SELECT * FROM markers WHERE 1";
    $result = mysqli_query($connection, $query);
    if (!$result) {
    die('Invalid query: ' . mysqli_error($connection));
    }

    // Iterate through the rows, adding XML nodes for each

    while ($row = @mysqli_fetch_assoc($result)){
    // Add to XML document node
    $node = $dom->createElement("marker");
    $newnode = $parnode->appendChild($node);
    $newnode->setAttribute("id",$row['id']);
    $newnode->setAttribute("name",$row['name']);
    $newnode->setAttribute("address", $row['address']);
    $newnode->setAttribute("lat", $row['lat']);
    $newnode->setAttribute("lng", $row['lng']);
    $newnode->setAttribute("type", $row['type']);
    }

    echo $dom->saveXML();
    wp_die();
}

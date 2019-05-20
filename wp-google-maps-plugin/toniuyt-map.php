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

function add_map()
{
    wp_enqueue_script('load_map', plugins_url('/js/load_map.js', __FILE__), array('jquery'), '', true);

    wp_localize_script('load_map', 'ipAjaxVar', array(
        'ajaxurl' => admin_url('admin-ajax.php')
    ));

    echo "<div id=\"map-container\" style=\"width:100%;height:500px;\"><div id=\"map\" style=\"width:80%;height:100%;float:left;\"></div>
        <div id=\"map-filters\" style=\"width:20%;float:left;height:100%;overflow-y:scroll;\">
        </div></div>
    <script async defer src=\"https://maps.googleapis.com/maps/api/js?key=API_KEY\"> </script>";
}

add_shortcode('google-map-fullscreen', 'add_map_fullscreen');

function add_map_fullscreen()
{
    wp_enqueue_script('autocomplete', plugins_url('/js/autocomplete.js', __FILE__), array('jquery'), '', true);
    wp_enqueue_script('load_map', plugins_url('/js/load_map.js', __FILE__), array('jquery'), '', true);
    wp_enqueue_style('map-theme', plugins_url('/css/style.css', __FILE__));

    wp_localize_script('load_map', 'ipAjaxVar', array(
        'ajaxurl' => admin_url('admin-ajax.php')
    ));

    echo "<div id=\"map\" style=\"width:100%;height:100%;\"></div>
    <script async defer src=\"https://maps.googleapis.com/maps/api/js?key=AIzaSyAR44uAYDTKFCmYsbc4FldE09-EE1iwKBQ\"> </script>";
}

add_action('wp_ajax_marker_filters', 'marker_filters');
add_action('wp_ajax_nopriv_post_marker_filters', 'marker_filters');
function marker_filters()
{
    require("dbinfo.php");
    $connection = mysqli_connect('localhost', $username, $password);
    $db_selected = mysqli_select_db($connection, $database);

    $query = "SELECT type FROM markers GROUP BY type;";
    $result = mysqli_query($connection, $query);
    if (!$result) {
        die('Invalid query: ' . mysqli_error($connection));
    }

    while ($row = @mysqli_fetch_assoc($result)) {
        echo $row['type'];
        echo ',';
    }
    wp_die();
}

add_action('wp_ajax_marker_xml', 'marker_xml');
add_action('wp_ajax_nopriv_post_marker_xml', 'marker_xml');
function marker_xml()
{
    require("dbinfo.php");

    $dom = new DOMDocument("1.0");
    $node = $dom->createElement("markers");
    $parnode = $dom->appendChild($node);

    // Opens a connection to a MySQL server
    $connection = mysqli_connect('localhost', $username, $password);
    if (!$connection) {
        die('Not connected : ' . mysqli_error($connection));
    }

    // Set the active MySQL database
    $db_selected = mysqli_select_db($connection, $database);
    if (!$db_selected) {
        die('Can\'t use db : ' . mysqli_error($connection));
    }

    $filter = $_POST['filter'];
    // Select all the rows in the markers table
    $query = "SELECT * FROM markers WHERE type = '".$filter."'";
    $result = mysqli_query($connection, $query);
    if (!$result) {
        die('Invalid query: ' . mysqli_error($connection));
    }

    // Iterate through the rows, adding XML nodes for each

    while ($row = @mysqli_fetch_assoc($result)) {
        // Add to XML document node
        $node = $dom->createElement("marker");
        $newnode = $parnode->appendChild($node);
        $newnode->setAttribute("id", $row['id']);
        $newnode->setAttribute("name", $row['name']);
        $newnode->setAttribute("address", $row['address']);
        $newnode->setAttribute("lat", $row['lat']);
        $newnode->setAttribute("lng", $row['lng']);
        $newnode->setAttribute("type", $row['type']);
    }

    echo $dom->saveXML();
    wp_die();
}

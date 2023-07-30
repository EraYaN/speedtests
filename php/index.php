<?php
ini_set("session.cookie_samesite", "None");
session_start();
date_default_timezone_set('Europe/Amsterdam');

define('DEBUG', false); // Debug OFF in production
define('CACHING', true); // Caching ON in production

require 'vendor/autoload.php';

require_once("slim-config.php");


require_once("endpoints.php");

// Run app
$app->run();

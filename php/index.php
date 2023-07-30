<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;

require 'vendor/autoload.php';

class Barcode
{
    public $Id;
    public $Code;
    public $Status;
}

enum BarcodeStatus
{
    case aangemaakt;
    case gedownload;
    case gebruikt;
    case retour;
    case vervallen;
}

/**
 * Instantiate App
 *
 * In order for the factory to work you need to ensure you have installed
 * a supported PSR-7 implementation of your choice e.g.: Slim PSR-7 and a supported
 * ServerRequest creator (included with Slim PSR-7)
 */
$app = AppFactory::create();

/**
 * The routing middleware should be added earlier than the ErrorMiddleware
 * Otherwise exceptions thrown from it will not be handled by the middleware
 */
$app->addRoutingMiddleware();

/**
 * Add Error Middleware
 *
 * @param bool                  $displayErrorDetails -> Should be set to false in production
 * @param bool                  $logErrors -> Parameter is passed to the default ErrorHandler
 * @param bool                  $logErrorDetails -> Display error details in error log
 * @param LoggerInterface|null  $logger -> Optional PSR-3 Logger  
 *
 * Note: This middleware should be added last. It will not handle any exceptions/errors
 * for middleware added after it.
 */
$errorMiddleware = $app->addErrorMiddleware(true, true, true);

// Define app routes
$app->get('/', function (Request $request, Response $response, $args) {
    $response->getBody()->write("This is an API server, please use the correct client.");
    return $response->withStatus(200);
});

$app->get('/barcode/lookup', function (Request $request, Response $response, $args) {
    $params = $request->getQueryParams();
    if (!empty($params['barcode'])) {
        $code = $params['barcode'];
        $mysqli = new mysqli("percona", "speedtest", "speedtest", "speedtest", 3306);
        $res = $mysqli->query("select barcode_id as id, barcode as code, status as status from barcodes where barcode = '" . $mysqli->real_escape_string($code) . "'", MYSQLI_STORE_RESULT);
        if ($res->num_rows == 1) {
            $dat = $res->fetch_assoc();
            $dat["id"] = intval($dat["id"]);
            $response->getBody()->write(json_encode($dat));
            return $response->withStatus(200)->withHeader('Content-Type', 'application/json');
        }
    }

    return $response->withStatus(404);
});

// Run app
$app->run();

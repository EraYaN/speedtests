<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

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


// Define app routes
$app->get('/', function (Request $request, Response $response, $args) {
    $response->getBody()->write("This is an API server, please use the correct client.");
    return $response->withStatus(200);
});

$app->get('/barcode/template', function (Request $request, Response $response, $args) {
    $params = $request->getQueryParams();
    if (!empty($params['barcode'])) {
        $code = $params['barcode'];
        $mysqli = $this->get('db');
        $res = $mysqli->query("select barcode_id as id, barcode as code, status as status from barcodes where barcode = '" . $mysqli->real_escape_string($code) . "'", MYSQLI_STORE_RESULT);
        if ($res->num_rows == 1) {
            $dat = $res->fetch_assoc();
            $dat["id"] = intval($dat["id"]);
            return $this->get('view')->render($response, 'barcode.twig', ['current_route_name' => \Slim\Routing\RouteContext::fromRequest($request)->getRoute()->getName(), 'barcode' => $dat]);
        }
    }

    throw new \Slim\Exception\HttpNotFoundException($request,"Barcode not found");
});

$app->get('/barcode/lookup', function (Request $request, Response $response, $args) {
    $params = $request->getQueryParams();
    if (!empty($params['barcode'])) {
        $code = $params['barcode'];
        $mysqli = $this->get('db');
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

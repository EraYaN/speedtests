<?php

use Slim\Factory\AppFactory;
use DI\Container;
use Slim\Http\Factory\DecoratedResponseFactory;
use Slim\Views\Twig;
use Slim\Views\TwigMiddleware;
use EraYaN\TicketAssist\Exceptions;
use EraYaN\TicketAssist\Middleware;

/**
 * Instantiate App
 *
 * In order for the factory to work you need to ensure you have installed
 * a supported PSR-7 implementation of your choice e.g.: Slim PSR-7 and a supported
 * ServerRequest creator (included with Slim PSR-7)
 */
$container = new Container();
$streamFactory = new \Slim\Psr7\Factory\StreamFactory();
AppFactory::setContainer($container);
AppFactory::setStreamFactory($streamFactory);
$app = AppFactory::create();



$container->set('settings', function (\Psr\Container\ContainerInterface $c) {
    $config = array();

    $config = [
        'debug' => DEBUG,
        'caching' => CACHING ? '/tmp/twig-cache' : false,
        'locale-cache' => CACHING ? '/tmp/locale-cache' : null,
        'routerCacheFile' => '/tmp/router-cache',

        'db' => [
            'host' => !empty($_SERVER['SQL_HOST']) ? $_SERVER['SQL_HOST'] : "percona",
            'user' => !empty($_SERVER['SQL_USER']) ? $_SERVER['SQL_USER'] : "root",
            'pass' => !empty($_SERVER['SQL_PASSWORD']) ? $_SERVER['SQL_PASSWORD'] : "testpassword",
            'dbname' => !empty($_SERVER['SQL_DATABASE']) ? $_SERVER['SQL_DATABASE'] : "speedtest",
        ],
    ];
    return $config;
});

if ($container->get('settings')['caching'] !== false) {
    $container->set('cache', function (\Psr\Container\ContainerInterface $c) {
        return new \Slim\HttpCache\CacheProvider();
    });

    $app->add(new \Slim\HttpCache\Cache('private', 0, true));

    $routeCollector = $app->getRouteCollector();
    $routeCollector->setCacheFile($container->get('settings')['routerCacheFile']);
}


$container->set('db', function (\Psr\Container\ContainerInterface $c) {
    $db = $c->get('settings')['db'];
    $link = mysqli_init();
    if (!$link) {
        throw new Exceptions\DatabaseException("MySQLI Init failed.\n");
    }
    $link->options(MYSQLI_OPT_INT_AND_FLOAT_NATIVE, true);
    if (!$link->real_connect($db['host'], $db['user'], $db['pass'], $db['dbname'])) {
        throw new Exceptions\DatabaseException("Error connecting to the database: " . $link->connect_error . "\n", $link->connect_errno);
    }
    if (!$link->set_charset('utf8mb4')) {
        throw new Exceptions\DatabaseException("Error loading character set utf8mb4: " . $link->error . "\n", $link->errno);
    }
    return $link;
});

$container->set('notFoundHandler', function (\Psr\Container\ContainerInterface $c) {
    return function ($request, $response) use ($c) {
        $uri = $request->getUri();
        return $c->get('view')
            ->render($response->withStatus(404), 'error/not-found.twig', array("method" => $request->getMethod(), "routeName" => $request->getAttribute('route') != null ? \Slim\Routing\RouteContext::fromRequest($request)->getRoute()->getName() : NULL, "path" => $uri->getPath(), "host" => $uri->getHost(), "query" => $uri->getQuery()));
    };
});

if (!$container->get('settings')['debug']) {
    $container->set('errorHandler', function (\Psr\Container\ContainerInterface $c) {
        return function ($request, $response, \Exception $exception) use ($c) {
            return $c['response']->withJSON(array('error' => "Server Exception", "message" => 'Something went wrong!', "method" => $request->getMethod(), "uri" => $request->getUri(), 'exception' => $exception->getMessage(), 'line' => $exception->getLine(), 'file' => $exception->getFile(), 'trace' => $exception->getTraceAsString()), 500);
        };
    });
    $container->set('phpErrorHandler', function (\Psr\Container\ContainerInterface $c) {
        return function ($request, $response, $error) use ($c) {
            if (empty($error)) {
                $error = "Internal Server Error";
            }
            return $c['response']
                ->withJSON(array("message" => 'Something went wrong!', "method" => $request->getMethod(), "uri" => $request->getUri(), 'error' => $error), 500);
        };
    });
}
$container->set(\Slim\Routing\RouteParser::class, $app->getRouteCollector()->getRouteParser());

if (class_exists('Twig\Sandbox\SecurityPolicy')) {
    /// Twig policy
    $global_tags = array('trans', 'if', 'set', 'verbatim', 'filter', 'for', 'with');
    $global_extra_tags = array('from', 'import', 'macro');
    $global_filters = array('upper', 'lower', 'date', 'date_modify', 'localizeddate', 'localizednumber', 'localizedcurrency', 'escape', 'capitalize', 'abs', 'first', 'format', 'nl2br', 'last', 'raw', 'sort', 'title', 'trim', 'striptags');
    $global_methods = array();
    $global_properties = array(
        'EraYaN\TicketAssist\Entities\Event' => array('Id', 'Description', 'ExtraInfo', 'AfterOrderInfo', 'Name', 'UrlName', 'Location', 'Done', 'Public', 'Highlight', 'HighlightCaption', 'AddressLine1', 'AddressLine2', 'PostalCode', 'City', 'Country', 'Organizer', 'PriceInfo', 'DateInfo', 'Acts', 'MinimumAgeInfo', 'Files'),
        'EraYaN\TicketAssist\Entities\Ticket' => array('Id', 'Description', 'StartTime', 'EndTime', 'StartTimeTZ', 'EndTimeTZ', 'Acts', 'Price', 'ServiceFees', 'MinimumAge', 'SalesStopTime', 'SalesStopTimeTZ', 'OnSale', 'InMainShop'),
        'EraYaN\TicketAssist\Entities\User' => array('Id', 'Name', 'Type', 'FirstName', 'LastName', 'Company', 'Email', 'Address', 'PostalCode', 'City', 'Phone', 'Description', 'Events'),
    );
    $global_functions = array('url_for', 'artistHeader');
    sort($global_tags);
    sort($global_filters);
    sort($global_functions);
    $global_policy = new \Twig\Sandbox\SecurityPolicy(array_merge($global_tags, $global_extra_tags), $global_filters, $global_methods, $global_properties, $global_functions);
    $global_policy_verify = new \Twig\Sandbox\SecurityPolicy($global_tags, $global_filters, $global_methods, $global_properties, $global_functions);
} else {
    //die('Security policy could not be defined.');
    $global_policy = false;
}

// Register Twig View helper
$container->set('view', function (\Psr\Container\ContainerInterface $c) {
    global $global_policy, $btd, $domain, $locale;
    if ($global_policy === false)
        die("No policy");
    $settings = $c->get('settings');
    $view = Twig::create('twig-templates', [
        'cache' => $settings['caching'],
        'debug' => $settings['debug']
    ]);

    $sandbox = new \Twig\Extension\SandboxExtension($global_policy);
    $view->addExtension($sandbox);
    $view->addExtension(new \Twig\Extension\StringLoaderExtension());

    if ($settings['debug'])
        $view->addExtension(new \Twig\Extension\DebugExtension());
    $twig_env = $view->getEnvironment();
    $twig_env->addGlobal('session', $_SESSION);

    return $view;
});

$container->set(DecoratedResponseFactory::class, new DecoratedResponseFactory($app->getResponseFactory(), $streamFactory));

$app->add(TwigMiddleware::createFromContainer($app));

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
$errorMiddleware = $app->addErrorMiddleware(DEBUG, true, true);

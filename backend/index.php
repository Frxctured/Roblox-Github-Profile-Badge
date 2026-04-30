<?php
require_once __DIR__ . '/vendor/autoload.php';

use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->safeLoad();

require_once 'api.php';

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if (preg_match('/^\/roblox\/github-badge\/user\/(.+)$/', $uri, $matches)) {
    $identifier = $matches[1];
    $userID = is_numeric($identifier) 
        ? (int)$identifier
        : get_id_from_username($identifier);

    get_status_badge($userID);
} 
elseif (preg_match('/^\/roblox\/github-badge\/redirect\/(.+)$/', $uri, $matches)) {
    $identifier = $matches[1];
    $userID = is_numeric($identifier) 
        ? (int)$identifier
        : get_id_from_username($identifier);

    header("Location: https://www.roblox.com/users/$userID/profile");
} 
else {
    http_response_code(404);
    echo json_encode(["error" => "404 Not Found"]);
}
?>

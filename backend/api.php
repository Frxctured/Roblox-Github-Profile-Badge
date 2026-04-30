<?php
$ROBLOSECURITY = $_ENV['ROBLOSECURITY'] ?? null;

function fetch_roblox($url, $method = 'GET', $payload = null, $cookie = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    }

    if ($cookie) {
        curl_setopt($ch, CURLOPT_COOKIE, ".ROBLOSECURITY=$cookie");
    }

    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function get_id_from_username($username) {
    $data = fetch_roblox("https://users.roblox.com/v1/usernames/users", 'POST', [
        "usernames" => [$username],
        "excludeBannedUsers" => true
    ]);
    return $data['data'][0]['id'] ?? -1;
}

function get_status_badge($userID) {
    global $ROBLOSECURITY;
    
    $presence = fetch_roblox("https://presence.roblox.com/v1/presence/users", 'POST', 
        ["userIds" => [(int)$userID]], $ROBLOSECURITY);
    $status_data = $presence['userPresences'][0] ?? null;

    $user_info = fetch_roblox("https://users.roblox.com/v1/users/$userID");
    $pfp_info = fetch_roblox("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=$userID&size=100x100&format=Png");
    
    $universeID = $status_data['universeId'] ?? 0;
    $game_info = fetch_roblox("https://games.roblox.com/v1/games?universeIds=$universeID&fields=name");
    
    $pfp_url = $pfp_info['data'][0]['imageUrl'] ?? "";
    $pfp_base64 = "data:image/png;base64," . base64_encode(file_get_contents($pfp_url));

    $status_map = [3 => "creating", 2 => "playing", 1 => "website", 0 => "offline"];
    $status_class = $status_map[$status_data['userPresenceType'] ?? 0];

    $template = file_get_contents(__DIR__ . "/assets/status.svg.template");
    $output = str_replace(
        ["{{displayname}}", "{{username}}", "{{pfp}}", "{{game}}", "{{status}}", "{{status_class}}"],
        [$user_info['displayName'], $user_info['name'], $pfp_base64, $game_info['data'][0]['name'], $status_class, $status_class],
        $template
    );

    header("Content-Type: image/svg+xml");
    header("Cache-Control: no-cache, no-store, must-revalidate");
    echo $output;
}
?>

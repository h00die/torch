<?php

function print_blockpage() {
    echo '<!DOCTYPE html> <html> <head lang="en"> <meta charset="UTF-8">
	<title>Unauthorized access</title>
	<link type="text/css" rel="stylesheet" href="/static/css/bootstrap-theme.min.css">
	<link type="text/css" rel="stylesheet" href="/static/css/main.css">
	<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
	</head>
	<body>
	<div class="header">
        <img class="logo" src="/static/img/logo.png">
	</div>
	<div class="container">
        <h2>SORRY</h2>

        <p>YOU\'RE NOT ALLOWED TO VISIT THIS SITE</p>
	</div>
	</body>
	</html>';
}

session_start();
$router_ip = gethostbyname($_SERVER['SERVER_ADDR']);

if (isset($_SESSION['dst']) && $_SESSION['dst'] != $router_ip ) {
    header('Location: http://'.$_SESSION['dst']);
    unset($_SESSION['dst']);
}
else if (! isset($_SESSION['dst'])) {
    $_SESSION['dst'] = $_GET['dst'];
}

print_blockpage();

?>
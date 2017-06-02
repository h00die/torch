<?php

function do_add_device($device_name) {

    $msg = 'Oops, we where not able to add your device. Login to <a href="http://home.mytorch.com">home.mytorch.com</a> and check your device';

    $ip_address = $_SERVER['REMOTE_ADDR'];
    if (array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER)) {
	$ip_address = array_pop(explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']));
    }

    if (!empty($device_name) && !empty($ip_address)) {
	$arg = escapeshellarg($ip_address).' '.escapeshellarg($device_name);
	// make call script with right params
	$rep = exec('/etc/torch/device_add '.$arg);
	$json = json_decode($rep, true);
	//sleep(2);
	if ($json["status"] == "ok") {
	    $url = exec('grep "torchdomain" /etc/config/torchdomains | cut -d= -f2');
	    //$_SESSION['url'] = $url."/device/setup";
    	    //header('Location: '.$url."/device/setup");
	    $msg = 'Your device was added successfully ! </br> <a href="http://home.mytorch.com/torch/dashboard/devices">Click here to finish profile configuration ...</a>';
	}
	else {
	    if ($json["status"] == "error") {
		$msg = $json["errors"][0]["message"];
	    }
	}
    }
    return '<label class="label">'.$msg.'</label>';
}


session_start();
$router_ip = gethostbyname($_SERVER['SERVER_ADDR']);

// default content
$content = '<form method="post" class="form" action="index.php">
<label class="label">What device is this ?</label>
<input type="text" class="input" name="name" id="name" required>
<input type="hidden" name="mac" value="">
<input type="hidden" name="ip" value="">
<input type="hidden" name="systemName" value="">
<div align="center">
<input class="submit" type="submit" value="Send" />
</div>
</form>';

if (isset($_POST['name'])) {
    $device_name = $_POST['name'];
    $content = do_add_device($device_name);
}
else if (isset($_SESSION['dst']) && !isset($_POST['name']) && $_SESSION['dst'] != $router_ip ) {
    header('Location: http://'.$_SESSION['dst']);
    unset($_SESSION['dst']);
}
else if (! isset($_SESSION['dst'])) {
    $_SESSION['dst'] = $_GET['dst'];
}

echo '<html class="">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>

<title>Setting up device</title>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">

<link type="text/css" rel="stylesheet" href="/static/css/main.css">
</head>

<body>


<div class="header">
<img class="logo" src="/static/img/logo.png">
</div>
<div class="content">'.$content.'</div>
</body>
</html>';

?>
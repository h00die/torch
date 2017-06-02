#!/usr/bin/php-cgi -q
<?php

$isDebug = false;
$javaTimeout = 5;
$mac = isset($argv[1]) or die("Mac is not found\n");
$host = isset($argv[2]) or die("API host is not found\n");
$mac = $argv[1];
$host = $argv[2];

function myLog($msg)
{
    global $isDebug;

    if ($isDebug) {
        shell_exec('logger -t "php" "' . $msg . '"');
    }
}

function myErrorLog($msg)
{

    shell_exec('logger -t "php ERROR:" "' . $msg . '"');
}

$stdOut = fopen('php://stdout', 'w'); //output handler
stream_set_timeout($stdOut, 86410);

function myResponse($msg)
{
    global $stdOut;
    fputs($stdOut, "$msg\n"); //writing output operation
    myLog("Sent: " . $msg);
}

$ports = [8081, 8082];
$portIndex = 0;
function getConnection()
{
    global $host, $ports, $portIndex, $javaTimeout;

    $count = 0;
    while (true) {
        $errNo = '';
        $errStr = '';
        $conn = @stream_socket_client("$host:" . $ports[$portIndex], $errNo, $errStr, $javaTimeout);
        if (!$conn) {
            myErrorLog("$errStr ($errNo)\n");
            $portIndex++;
            $count++;
            if (!isset($ports[$portIndex])) {
                $portIndex = 0;
            }

            if ($count >= count($ports)) {
                break;
            }
            continue;
        }
        return $conn;
    }
    return null;
}

$stdIn = fopen('php://stdin', 'r');
stream_set_timeout($stdIn, 86400);

while ($input = fgets($stdIn)) {
    myLog("Request: " . $input);

    $temp = array();
    $temp = explode(' ', $input);
    $status = $temp[0];

    try {
        $url = $temp[1];
        $device = explode("/", $temp[2])[0];
        $isHttps = 1;
        $pos = strrpos($url, ":443");
        if ($pos === false) { // note: three equal signs
            $isHttps = 0;
        }
        myLog("URL: " . $url);
        myLog("DEVICE: " . $device);

        $time = microtime(true);

        $javaConnect = getConnection();
        if ($javaConnect) {
            $request = [];
            $request["rmac"] = $mac;
            $request["dmac"] = $device;
            $request["action"] = 'access';
            $request["url"] = $url;
            $request["size"] = 0;
            $request["ps"] = $isHttps;
            $request = json_encode($request) . "\r\n";
            myLog("Java request:" . $request);

            fwrite($javaConnect, $request);
            if (!feof($javaConnect)) {
                $response = fgets($javaConnect, 8192);
                myLog("Response: " . $response);

                myLog((microtime(true) - $time) . ' elapsed');

                if (!$response) {
                    myErrorLog('Error in response');
                    myResponse("0");
                    continue;
                }

                $response = json_decode($response, true);

                if ($response["hstatus"] == 302) {
                    myLog("REDIRECT: " . $response["url"]);
                    myResponse("0 " . $response["url"]);
                    continue;
                }
            }
        }

        //error and success
        myResponse("0");
    } catch (Exception $e) {
        myLog("ERROR: " . $e->getMessage());
        myResponse("0");
    } finally {
        if ($javaConnect) {
            fclose($javaConnect);
        }
    }
} //while

fclose($stdIn);
fclose($stdOut);

//echo "url_rewrite_program /root/redirector.php" >> $CFGFILE
//chmod 777 ./redirector.php

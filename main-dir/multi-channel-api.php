<!-- 
multi-channel-api.php

This file triggers bash-scripts based on a url string. Simply navigate your browser or use
cURL or some other method to pass in URL params to trigger corresponding scripts. 

*Be sure to update the directory on line 35 to your directory path:
chdir('/home/justin/channels/');

To use: 
1) Install PHP
sudo apt install php

2) Run screen (so you can start a simple php server and exit the console):
screen

3) Navigate your directory with all the channels (i.e. /home/pi/channels/), and run a simple php server:
php -S 192.168.1.112:8080
-Make sure to update the IP:PORT to your client IP and whatever port you want to use/is open.

4) Trigger a bash script by navigating to your IP:PORT/multi-channel-api.php/?command=THE_COMMAND:
http://192.168.1.112:8080/multi-channel-api.php/?command=KEY_CHANNELUP

or use cURL: curl -I --request GET http://192.168.1.112:8080/?command=KEY_CHANNELUP
-->
<?php
header("HTTP/1.1 200 OK");
if (isset($_GET['command'])) {
    echo $_GET['command'];
    $command = $_GET['command'];
} else {
    // Fallback behaviour goes here
}
$old_path = getcwd();
chdir('/home/justin/channels/');
if ($command == "KEY_PLAY"){
	$output = shell_exec('bash ./manual.sh 01');
} else if ($command == "KEY_STOP"){
	$output = shell_exec('bash ./stop-all-channels.sh');
} else if ($command == "KEY_CHANNELUP"){
	$output = shell_exec('bash ./channelup.sh');
} else if ($command == "KEY_CHANNELDOWN"){
	$output = shell_exec('bash ./channeldown.sh');
} else if ($command == "KEY_1"){
	$output = shell_exec('bash ./manual.sh 01');
} else if ($command == "KEY_2"){
	$output = shell_exec('bash ./manual.sh 02');
} else if ($command == "KEY_3"){
	$output = shell_exec('bash ./manual.sh 03');
} else if ($command == "KEY_4"){
	$output = shell_exec('bash ./manual.sh 04');
} else if ($command == "KEY_5"){
	$output = shell_exec('bash ./manual.sh 05');
} else if ($command == "KEY_6"){
	$output = shell_exec('bash ./manual.sh 06');
} else if ($command == "KEY_7"){
	$output = shell_exec('bash ./manual.sh 07');
} else if ($command == "KEY_8"){
	$output = shell_exec('bash ./manual.sh 08');
} else if ($command == "KEY_9"){
	$output = shell_exec('bash ./manual.sh 09');
} else {
	//$output = shell_exec('./manual.sh 01');
}
chdir($old_path);
echo "<pre>$output</pre>";
?>

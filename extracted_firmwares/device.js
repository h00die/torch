function addDevice() {
    deviceName = document.getElementById("name").value;
    if (socket_di.readyState==1) {
	socket_di.send(deviceName);
	//alert('msg = ' + response);
    }
    return false;    
}

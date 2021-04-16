//  ENVISIoN
//
//  Copyright (c) 2019 Jesper Ericsson
//  All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are met:
//
//  1. Redistributions of source code must retain the above copyright notice, this
//  list of conditions and the following disclaimer.
//  2. Redistributions in binary form must reproduce the above copyright notice,
//  this list of conditions and the following disclaimer in the documentation
//  and/or other materials provided with the distribution.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
//  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
//  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
//  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
//  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
//  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
//  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
//  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
//  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// ##############################################################################################

const spawn = require("child_process").spawn;
const CONFIG = require("./config.json");
const {remote} = require('electron');
dialog = remote.dialog;

var pythonProcess = null

var nRequests = 0;
var nResponses = 0;
var nPings = 0

//TODO: not sure if encoding will always be the same on platforms

var response_callbacks = {
}

function start_python_process() {
    if (pythonProcess == null)
    {
        console.log("Starting python")
        if (window.navigator.platform == "Win32")
            pythonProcess = spawn('python', ["ElectronUI/nodeInterface.py"]);
        else
            pythonProcess = spawn('python3', ["ElectronUI/nodeInterface.py"]);
        console.log(pythonProcess)
        pythonProcess.stdout.on('data', on_data_recieve)
        pythonProcess.stderr.on('data', on_python_error)
        // pythonProcess.stdin.setEncoding('utf-8')
        // pythonProcess.stdout.pipe(process.stdout);
    }
    else {
        console.log("Python process already launched")
    }

    // Send a ping every second to keep checking that python is responsive
    setInterval(()=>send_data('ping', nPings++), 1000)
}



function send_request(type, parameters=null) {
    // Send a default envision request
    if (parameters == null) parameters = []
    nRequests += 1;
    responsesBehind(nRequests - nResponses);
    send_data('request', {type: type, parameters: parameters})
}

function send_data(tag, data) {
// Put data into json object and send it
    if (pythonCrashed)
        return;
    var json_data = {tag: tag, data: data}
    var packet = JSON.stringify(json_data) + "\r\n";
    try{
        if (CONFIG.logSentPackets && (tag != 'ping' || CONFIG.logPings))
            console.log("Sending packet: \n", packet)
	    pythonProcess.stdin.write(packet)
	}
    catch {
        alert()
        pythonCrashed = true;
		const options = {
			type: "warning", title: "ENVISIoN has stopped working!",
			message: "The python process has crashed. You must reload ENVISIoN or close and restart the program."
        }
		dialog.showMessageBox(options)
	}
}

function on_data_recieve(packet) {
    // Run when text is recieved from python. Decodes and reacts to packet data.

    // Split each line that was recieved
    data = Buffer.from(packet, 'hex')
    data = data.toString().split("\n")
    for (i = 0; i < data.length - 1; i++) {
        try {
            json_data = JSON.parse(data[i])
            if ("tag" in json_data){
                if (CONFIG.logRecievedPackets && (json_data['tag'] != 'pong' || CONFIG.logPings))
                    console.log("Packet recieved:\n", JSON.stringify(json_data))

                if (json_data["tag"] == "response"){
                    handle_response_packet(json_data["data"])
                    nResponses += 1;
                    responsesBehind(nRequests - nResponses);
                }
                else if (json_data["tag"] == "error"){
                    nResponses += 1;
                    responsesBehind(nRequests - nResponses);
                    let req = JSON.stringify(json_data['data'][0])
                    let error = json_data['data'][1]
                    let errorType = error[0];
                    let errorDesc = error[1].replace(/\\n/g, "\n");
                    let options = {
                        type: "error", title: "Request failed to resolve.",
                        message: errorType + "\n" + errorDesc + "\n" + req
                    }
                    dialog.showMessageBox(options)
                }
                else if (json_data["tag"] == "pong") {
                    // console.log('Ping: ' + json_data['data'])
                }
            }
            else{
                if (CONFIG.logPyPrint)
                    console.log("Python print: \n" + data[i])
            }
        }

        // Packet could not be decoded as json.
        catch(err) {
            if (CONFIG.logPyPrint)
                console.log("Python print: \n" + data[i])
        }
    }
}

function set_response_callback(type, func) {
    response_callbacks[type] = func;
}

function handle_response_packet(packet){
    let type = packet['type'];
    let data = packet['data'];
    if (type in response_callbacks && typeof response_callbacks[type] == 'function'){
        response_callbacks[type](...data);
    }
}

var pythonCrashed = false;
var lastError;
function on_python_error(data) {
    //lastError = Buffer.from(data, 'hex')
    // setTimeout(function(){
    //     nRequests--;
    //     send_data("crash test", "");
    //     }, 1000);
    if (!CONFIG.logPyError)
        return
    console.log("PYTHON ERROR: ")
    console.log(data.toString())
    // var output = Buffer.from(data, 'hex')
    //dialog.showErrorBox("Error in ENVISIoN: ", data.toString())
}

var loadingTimeout = null;
var dismissTimeout = null;
function responsesBehind(n){
    if (n <= 0 && dismissTimeout == null){
        clearTimeout(loadingTimeout)
        loadingTimeout = null;
        dismissTimeout = setTimeout(function(){$("#loadalert").slideUp(500);}, 800);
    }
    else if (loadingTimeout == null){
        clearTimeout(dismissTimeout)
        dismissTimeout = null;
        loadingTimeout = setTimeout(function(){$("#loadalert").slideDown(500);}, 800);
    }
    $("#loadalert > span").text(" envision is " + n + " requests behind.");
}

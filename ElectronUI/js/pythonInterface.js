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

var pythonProcess = null

var nRequests = 0;
var nResponses = 0;

//TODO: not sure if encoding will always be the same on platforms

var response_callbacks = {
    // "start": visualisationStarted,
    // "get_bands": loadBands,
    // "get_atom_names": loadAtoms,
    // "get_tf_points": loadTFPoints,
    // "get_available_datasets": loadAvailableDatasets,
    "get_ui_data": uiDataRecieved,
    "start": visualisationStarted,
    "stop": visualisationStopped
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
}

function send_test_packets(n){
    for (i = 0; i < n; i++) {
        send_data("Message", "Here be packets.")
    } 
}

function send_data(tag, data) {
// Put data into json object and send it
    nRequests += 1;
    responsesBehind(nRequests - nResponses);
    if (pythonCrashed)
        return;
    var json_data = {type: tag, data: data}
    var packet = JSON.stringify(json_data) + "\r\n";
    try{
        if (CONFIG.logSentPackets) console.log("Sending packet: \n", packet)
        pythonProcess.stdin.write(packet) 
    }
    catch {
        pythonCrashed = true;
        alert("ENVISIoN crashed!\nThe python process of envision has crashed. You must restart envision to fix this.");
    }
}

function on_data_recieve(packet) {
    // Print data recieved from python process  

    // Decode data
    data = Buffer.from(packet, 'hex')
    // // Split up if multiple JSON objects were recieved
    data = data.toString().split("\n")
    for (i = 0; i < data.length - 1; i++) {
        try {
            json_data = JSON.parse(data[i])
            if ("type" in json_data){
                if (CONFIG.logRecievedPackets)
                console.log("Packet recieved: \n", JSON.stringify(json_data))
                if (json_data["type"] == "response"){
                    handle_response_packet(json_data["data"])
                    nResponses += 1;
                    responsesBehind(nRequests - nResponses);
                }
            }
            else{
                if (CONFIG.logPyPrint)
                    console.log("Python print: \n" + data[i])
            }
            
          }
          catch(err) {
            if (CONFIG.logPyPrint)
                console.log("Python print: \n" + data[i])
          } 
    }
}

function handle_response_packet(packet){
    let action = packet[0];
    let status = packet[1];
    let id = packet[2]
    let data = packet[3];
    if (action in response_callbacks){
        response_callbacks[action](status, id, data);
    }
    if (!status && CONFIG.logFailedRequests){
        let errorType = data[0];
        let errorMsg = data[1].replace(/\\n/g, "\n");
        console.log("Requested action failed: \n" + errorType + ": " + errorMsg);
        if (errorType != "HandlerNotFoundError"){
            alert(errorType + "\n" + errorMsg);
        }
        // alert(data.replace(/\\n/g, "\n"));
        // console.log(data.replace(/\\n/g, "\n"));
    }
}

var lastError;
var pythonCrashed = false;
function on_python_error(data) {
    lastError = Buffer.from(data, 'hex')
    // setTimeout(function(){
    //     nRequests--;
    //     send_data("crash test", "");
    //     }, 1000);
    if (!CONFIG.logPyError)
        return
    console.log("PYTHON ERROR: ")
    var output = Buffer.from(data, 'hex')
    console.log(data.toString());
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





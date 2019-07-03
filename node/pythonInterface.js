//  Created by Jesper Ericsson
//
//  To the extent possible under law, the person who associated CC0
//  with the alterations to this file has waived all copyright and related
//  or neighboring rights to the alterations made to this file.
//
//  You should have received a copy of the CC0 legalcode along with
//  this work.  If not, see
//  <http://creativecommons.org/publicdomain/zero/1.0/>.

const spawn = require("child_process").spawn;

const LOG_PYTHON_PRINT = false
const LOG_PYTHON_ERROR = false

var pythonProcess = null

//TODO: not sure if encoding will always be the same on platforms

function start_python_process() {
    if (pythonProcess == null)
    {
        console.log("Starting python")
        pythonProcess = spawn('/usr/bin/python3', ["py_js_networking.py"]);
        // console.log(pythonProcess)
        pythonProcess.stdout.on('data', on_data_recieve)
        pythonProcess.stderr.on('data', on_python_error)
        // pythonProcess.stdin.setEncoding('utf-8')
        // pythonProcess.stdout.pipe(process.stdout);
    }
    else {
        console.log("Python process already launched")
    }
}

function one_greeting(){
    send_data("Greeting", "Hello from node.")
}
function lotsa_messages() {
    for (i = 0; i < 100; i++) {
        send_data("Message", "Here be data")
    } 
}

function start_charge_vis() {
    send_data("envision request", ["start vis", "charge"])
}

function stop_vis(){
    send_data("envision request", ["stop vis", "all"])
}

function random_color(){
    send_data(
        "envision request",  
        ["edit", ["charge", "add tf point", [Math.random(), Math.random(), Math.random(), Math.random()]]])
}

function send_data(tag, data) {
// Put data into json object and send it
    // console.log("sending data")
    var json_data = {type: tag, data: data}
    var packet = JSON.stringify(json_data) + "\r\n"
    pythonProcess.stdin.write(packet) 
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
            console.log(JSON.stringify(json_data))
          }
          catch(err) {
            if (LOG_PYTHON_PRINT)
                console.log("Python print: " + data[i])
          } 
    }
}

function on_python_error(data) {
    if (!LOG_PYTHON_ERROR)
        return
    console.log("PYTHON ERROR: ")
    var output = Buffer.from(data, 'hex')
    console.log(data.toString());
}



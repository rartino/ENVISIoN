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

var LOG_PYTHON_PRINT = false
var LOG_PYTHON_ERROR = true
var LOG_SENT_PACKAGES = true

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

function custom_action(){
    var entry = document.getElementById("command_line").value
    var words = entry.split(" ")
    var action = words[0]
    var target = words[1]
    var params = entry.substr(entry.indexOf(" ") + 1);
    params = params.substr(params.indexOf(" ") + 1);
    params = JSON.parse(params)
    send_data("envision request", [action, target, params])
}
function one_greeting(){
    send_data("Greeting", "Hello from node!")
}
function lotsa_messages() {
    for (i = 0; i < 100; i++) {
        send_data("Message", "Let there be packets.")
    } 
}

function start_charge_vis() {
    send_data("envision request", ["start", "charge", ["charge", "/home/labb/HDF5/nacl_new.hdf5"]])
}

function stop_vis(){
    send_data(
        "envision request",
        ["stop", "-", [true]]
    )
}

function random_color(){
    send_data(
        "envision request",  
        ["add_tf_point", "charge", [Math.random(), [Math.random(), Math.random(), Math.random(), Math.random()]]])
}

function extra_button(){
    send_data(
        "envision request",
        ["get_bands", "charge", "/home/labb/HDF5/nacl_new.hdf5"]
    )
}

function send_data(tag, data) {
// Put data into json object and send it
    var json_data = {type: tag, data: data}
    var packet = JSON.stringify(json_data) + "\r\n"
    pythonProcess.stdin.write(packet) 
    if (LOG_SENT_PACKAGES)
        console.log("Packet sent: \n", packet)
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
            console.log("Packet recieved: \n", JSON.stringify(json_data))
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



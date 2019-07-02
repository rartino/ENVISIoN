const spawn = require("child_process").spawn;

var pythonProcess = null

//TODO: not sure if encoding will always be the same on platforms

function start_python_process() {
    if (pythonProcess == null)
    {
        console.log("Starting python")
        pythonProcess = spawn('/usr/bin/python3', ["script.py"]);
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

function two_goodbyes(){
    send_data("Bye", "Goodbye")
    send_data("Bye", "Seeya")
}

function three_things(){
    send_data("Thing", "qwqw")
    send_data("Thing", "asas")
    send_data("Thing", "zxzx")
}

function lotsa_messages() {
    for (i = 0; i < 100; i++) {
        send_data("Message", "Here be data")
    } 
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
        json_data = JSON.parse(data[i])
        console.log(JSON.stringify(json_data))
    }
}

function on_python_error(data) {
    console.log("PYTHON ERROR: ")
    var output = Buffer.from(data, 'hex')
    console.log(data.toString());
}



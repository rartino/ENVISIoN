#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################

import sys, os, inspect
import time
import select
import json
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
from envisionpy.EnvisionMain import EnvisionMain
from envisionpy.utils.exceptions import *


import threading
import queue

def send_packet(tag, data):
# Package data into JSON-string-packet and send it via printing.
    packet = json.dumps({"tag": tag, "data": data})
    print(packet)
    sys.stdout.flush()

def decode_packet(packet):
# Return python dictionary based on JSON-string-packet
    obj = json.loads(packet)
    return obj

def input_loop(input_queue):
    while True:
        input_queue.put(sys.stdin.readline())

def main():
    input_queue = queue.Queue()

    input_thread = threading.Thread(target=input_loop, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    while True:
        time_start = time.time()
        while not input_queue.empty():
            # send_packet("Debug", "Packet recieved")
            packet = decode_packet(input_queue.get())
            if packet['tag'] == 'request':
                try: 
                    response = envisionMain.handle_request(packet['data'])
                    send_packet('response', response)
                except EnvisionError as e: # non critical error envision should still function.
                    send_packet('error', [packet['data'], format_error(e)])
                # except Exception as e:
                #     send_packet('error', [packet['data'], format_error(e)])
            if packet['tag'] == 'ping':
                send_packet('pong', packet['data'])
            else:
                print('Unhandled packet: ', packet)
        envisionMain.update()

        # Try to loop at 60 fps
        time_elapsed = time.time() - time_start
        time.sleep(max([1.0/60.0 - time_elapsed, 0]))

# Initialize ENVISIoN
send_packet("status", ["Initializing envision"])
envisionMain = EnvisionMain()
send_packet("status", ["envision started"])
# envisionMain.update()
# print(envisionMain.handle_request({'type': 'init_manager', 'data': ['C:/Kandidatprojekt/ENVISIoN-2020/nacl100.hdf5']}))
# envisionMain.update()
# print(envisionMain.handle_request({'type': 'start_visualisation', 'data': ['nacl100', 'charge']}))
# envisionMain.update()
# envisionMain.update()
# while True:
#     time_start = time.time()
#     envisionMain.update()

#     # Try to loop at 60 fps
#     time_elapsed = time.time() - time_start
#     time.sleep(max([1.0/60.0 - time_elapsed, 0]))



main()
    

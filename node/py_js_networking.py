#  Created by Jesper Ericsson
# 
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
# 
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
import sys
import time
import select
import json

from ENVISIoN_backend import ENVISIoN


# TODO: select method for checking if input is empty will not work on windows.

def send_packet(tag, data):
    packet = json.dumps({"type": tag, "data": data})
    print(packet)
    sys.stdout.flush()

def decode_packet(packet):
    # Process recieved data.
    obj = json.loads(packet)
    return obj

def process_packet(packet):
    data = decode_packet(packet)
    send_packet("Echo", data)

env = ENVISIoN()

while True:
    time.sleep(1.0/20)
    env.update()

    while select.select([sys.stdin,],[],[],0.0)[0]:
        # print(sys.stdin.readline())
        # send_packet("Debug", "Input recieved")
        process_packet(sys.stdin.readline())
        # decode_data(input())
    # else:
    #     send_data("Debug", "No input recieved")
    #     print("No input recieved")


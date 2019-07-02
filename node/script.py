import sys
import time
import select
import json

sys.path.append("/home/labb/Inviwo-latest/build/bin")
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


while True:
    time.sleep(1.0/20)

    while select.select([sys.stdin,],[],[],0.0)[0]:
        # print(sys.stdin.readline())
        # send_packet("Debug", "Input recieved")
        process_packet(sys.stdin.readline())
        # decode_data(input())
    # else:
    #     send_data("Debug", "No input recieved")
    #     print("No input recieved")


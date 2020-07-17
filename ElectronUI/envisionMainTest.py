import sys, os, inspect
import time
import select
import json
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
from envisionpy.EnvisionMain import EnvisionMain


import threading
import queue

def send_request(rtype, data):
    return envisionMain.handle_request({'type': rtype, 'data': data})

    

# Initialize ENVISIoN
envisionMain = EnvisionMain()

envisionMain.update()

print("Careful ahead")
del envisionMain.app
print("1")
del envisionMain
print("2")
# cidentifier = send_request('init_manager', ['C:/Kandidatprojekt/ENVISIoN-2020/nacl100.hdf5'])
# print(cidentifier)
# envisionMain.update()
# cidentifier = send_request('start_visualisation', ['nacl100', 'charge'])
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# envisionMain.update()
# while True:
#     time_start = time.time()
#     envisionMain.update()

#     # Try to loop at 60 fps
#     time_elapsed = time.time() - time_start
#     time.sleep(max([1.0/60.0 - time_elapsed, 0]))

# print("Deleting")
# del envisionMain
# print("Deleted")
while True:
    time.sleep(1)

# send_packet("status", ["envision started", True])

# main()
    

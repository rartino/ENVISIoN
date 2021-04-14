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
    return envisionMain.handle_request({'type': rtype, 'parameters': data})



# Initialize ENVISIoN
envisionMain = EnvisionMain()
envisionMain.update()
envisionMain.parse_vasp("TiPO4_bandstructure", "testEMT.hdf5","All")
#envisionMain.parse_vasp("TiPO4_bandstructure", "testEMT.hdf5",["Force"])
envisionMain.update()
send_request('init_manager', ['testEMT.hdf5'])
envisionMain.update()
send_request('start_visualisation', ['testEMT', 'force'])
envisionMain.update()
send_request("visualisation_request", ['testEMT', 'force', "disable_force", 'True'])#, True])
envisionMain.update()
#print("Careful ahead")
#del envisionMain.app
#print("1")
#del envisionMain
#print("2")
#cidentifier =
#print(cidentifier)

#envisionMain.init_manager("force_test.hdf5", identifier=None)
#cidentifier = send_request('start_visualisation', ['force_test', 'force'])
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#envisionMain.update()
#while True:
#    time_start = time.time()
#    envisionMain.update()

#     # Try to loop at 60 fps
#    time_elapsed = time.time() - time_start
#    time.sleep(max([1.0/60.0 - time_elapsed, 0]))

# print("Deleting")
# del envisionMain
# print("Deleted")
while True:
    time.sleep(0.5)
    envisionMain.update()

# send_packet("status", ["envision started", True])

# main()

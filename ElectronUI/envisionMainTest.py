import sys, os, inspect
import time
import select
import json
import PySimpleGUI as sg
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
#envisionMain.parse_ELK("CuFeS2", "testEMT.hdf5",["Unitcell"])
envisionMain.parse_vasp("TiPO4_bandstructure", "testEMT.hdf5","All")
envisionMain.update()
#send_request('init_manager', ['testEMT.hdf5'])
#envisionMain.update()
#send_request('start_visualisation', ['testEMT', 'force'])
#envisionMain.update()
#send_request("visualisation_request", ['testEMT', 'force', "disable_force", 'True'])#, True])
#envisionMain.update()
#send_request('visualisation_request', ["testEMT", "force", "show", []])
#envisionMain.update()
#send_request("visualisation_request", ["testEMT", "force", "hide_vectors"])
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
#while True:
#    envisionMain.update()
#    send_request("visualisation_request", ["testEMT", "force", "hide_vectors"])
#    envisionMain.update()
#    time.sleep(1)
#    send_request("visualisation_request", ["testEMT", "force", "show_vectors"])
#    envisionMain.update()
#    time.sleep(1)
# send_packet("status", ["envision started", True])

# main()

text = ['TiPO4_bandstructure', 'LiC_pair_corr_func']
a = [path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure", 'liC']

layout = [
    [sg.Text('Choose the VASP')]] + [
    [sg.Radio(text[i], 'VASP', enable_events=True, key=a[i])]
        for i in range(len(a))] + [[sg.Button('Cancel')] + [sg.Button('PARSE')]]

window = sg.Window('test', layout)

def parse(vasp, hdf5, type):
    envisionMain.update()
    envisionMain.parse_vasp(vasp, hdf5, type)
    envisionMain.update()
#parse("TiPO4_bandstructure", "test2.hdf5",["Unitcell"])
def find_selection_parse(values):
    for key, value in values.items():
        if value:
            return key

    return False


while True :

    event, values = window.read()
    if event == 'PARSE':
        if find_selection_parse(values):
            print('Selection made')
        else:
            print('Select a VASP_DIR')
    if event in (sg.WINDOW_CLOSED, 'Cancel'):
        break

window.close()
#parse("Cu_band_CUB", "test1234.hdf5",["Unitcell"])

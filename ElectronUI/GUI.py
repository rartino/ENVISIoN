import sys, os, inspect
import time
import select
import json
import random as rd
import PySimpleGUI as sg
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
from envisionpy.EnvisionMain import EnvisionMain

import threading
import queue

def send_request(rtype, data):
    return envisionMain.handle_request({'type': rtype, 'parameters': data})

#sys.stdout = open(os.devnull, "w")
#sys.stderr = open(os.devnull, "w")

canvas = True
vectors = True
back_color = 'pink'
t_color = 'black'
# Initialize ENVISIoN
envisionMain = EnvisionMain()

text = ['TiPO4_bandstructure',
        'NaCl_charge_density',
        'Animation',
        'Cu_band_CUB',
        'CuFeS2_band_CBT2',
        'LiC_pair_corr_func',
        'partial_charges',
        'TiO2_band_TET',
        'TiPO4_DoS',
        'TiPO4_ELF']

vasp_dir = [path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure",
            path_to_current_folder + "/../unit_testing/resources/NaCl_charge_density",
            path_to_current_folder + "/../unit_testing/resources/Animation",
            path_to_current_folder + "/../unit_testing/resources/Cu_band_CUB",
            path_to_current_folder + "/../unit_testing/resources/CuFeS2_band_CBT2",
            path_to_current_folder + "/../unit_testing/resources/LiC_pair_corr_func",
            path_to_current_folder + "/../unit_testing/resources/partial_charges",
            path_to_current_folder + "/../unit_testing/resources/TiO2_band_TET",
            path_to_current_folder + "/../unit_testing/resources/TiPO4_DoS",
            path_to_current_folder + "/../unit_testing/resources/TiPO4_ELF"]

visualisations = ['Force',
                 'Molecular Dynamics',
                 'Atom Positions',
                 'Charge Density',
                 'ELF']

visualisations_t = ('Force',
                 'Molecular Dynamics',
                 'Atom Positions',
                 'Charge Density',
                 'ELF')

force_attr = ['Toggle Canvas',
              'Toggle Force Vectors']

moldyn_attr = ['Toggle Canvas',
               'Play/Pause',
               'Change Color']

atom_attr = ['Toggle Canvas']


charge_attr = ['Toggle Canvas']

elf_attr = ['Toggle Canvas']

visualisations_d = {'Force' : force_attr,
                    'Molecular Dynamics' : moldyn_attr,
                    'Atom Positions' : atom_attr,
                    'Charge Density' : charge_attr,
                    'ELF' : elf_attr}

envisonMain_equivalent = {'Force' : 'force',
                          'Molecular Dynamics' : 'molecular_dynamics',
                          'Atom Positions' : 'atom',
                          'Charge Density' : 'charge',
                          'ELF' : 'elf'}

attr = ['Toggle Canvas',
        'Toggle Force Vectors',
        'Play/Pause',
        'Change Color']

attr_keys = ('opt0', 'opt1', 'opt2', 'opt3')

layout = [[
    [sg.Text('Choose the VASP', background_color = back_color, text_color = t_color)]],
    [[sg.Radio(text[i], 'VASP', enable_events=True, key=vasp_dir[i], background_color = back_color, text_color = t_color)] for i in range(len(vasp_dir))],
    [[sg.Button('Parse', button_color = 'green')]],
    [[sg.Text(text = ' '*80 + '\n' + ' '*80 + '\n' + ' '*80, key = 'parse_status', background_color = back_color, text_color = t_color)]],
    [[sg.Text('Choose what you want to visualize: ', background_color = back_color, text_color = t_color)]],
    [[sg.Button('Force'), sg.Button('Molecular Dynamics'), sg.Button('Atom Positions'), sg.Button('Charge Density'), sg.Button('ELF')]],
    [[sg.Button('1', key = 'opt0', enable_events=True, visible = False), sg.Button('2', key = 'opt1', visible = False), sg.Button('3', key = 'opt2', visible = False), sg.Button('4', key = 'opt3', visible = False)]],
    [[sg.Button('Exit', button_color = 'red')]],
    [[sg.Multiline(default_text='Welcome to GUI Numero Dos', key = 'textbox',size=(35, 6), no_scrollbar = True, autoscroll = True, write_only = True)]]]




window = sg.Window('GUI',layout, background_color = back_color)
active_dataset = False
last_vis = None
active_vis = ''


def parse(vasp_dir):
    try:
        envisionMain.update()
        envisionMain.parse_vasp(vasp_dir, path_to_current_folder + '/../GUI.hdf5','All')
        envisionMain.update()
        send_request('init_manager', [path_to_current_folder + '/../GUI.hdf5'])
        envisionMain.update()
    except:
        pass

def toggle_canvas(type):
    global canvas
    try:
        if canvas:
            envisionMain.update()
            send_request('visualisation_request', ["GUI", type, "hide", []])
            envisionMain.update()
            canvas = False
        else:
            envisionMain.update()
            send_request('visualisation_request', ["GUI", type, "show", []])
            envisionMain.update()
            canvas = True
        console_message('Canvas Toggled')
    except:
        pass
    return

def toggle_force_vectors(type):
    global vectors
    try:
        if type == 'force':
            if vectors:
                envisionMain.update()
                send_request("visualisation_request", ["GUI", type, "hide_vectors"])
                envisionMain.update()
                vectors = False
            else:
                envisionMain.update()
                send_request("visualisation_request", ["GUI", type, "show_vectors"])
                envisionMain.update()
                vectors = True
        else:
            pass
        console_message('Vectors Toggled')
    except:
        pass
    return

def unfinished(type):
    console_message('Not yet implemented')
    return

def console_message(msg):
    window['textbox'].Update('\n' + msg, append = True)
    return

def start_visualisation(type):
    envisionMain.update()
    send_request('start_visualisation', ['GUI', type])
    envisionMain.update()

def stop_visualisation(type):
    try:
        envisionMain.update()
        send_request('stop_visualisation', ['GUI', type])
        envisionMain.update()
    except:
        pass

def find_selection_parse(values):
    for key, value in values.items():
        if value:
            return key
    return False

def create_vis_attributes(attr):
    for i in range(len(attr)):
        window.FindElement('opt' + str(i)).Update(text = attr[i], visible = True, button_color = 'green')
    p = len(attr)
    while p < 4:
        window.FindElement('opt' + str(p)).Update(visible = False, button_color = 'green')
        p += 1
    return

def parse_progress_bar(vasp_dir):
    stop1 = rd.randint(10,30)
    stop2 = rd.randint(40,60)
    stop3 = rd.randint(70,90)
    lenght = 100
    layout = [[sg.Text('Working on it')],
          [sg.ProgressBar(lenght, orientation='h', size=(20, 20), key='progressbar')],
          [sg.Cancel()]]
    window2 = sg.Window('', layout)
    progress_bar = window2['progressbar']
    for i in range(lenght):
        event, values = window2.read(timeout=10)
        if i == stop1:
            time.sleep(0.4)
        if i == stop2:
            parse(vasp_dir)
        if i == stop3:
            time.sleep(0.3)
        if event == 'Cancel'  or event == sg.WIN_CLOSED:
            break
        progress_bar.UpdateBar(i + 1)
    window2.close()
    return True

def disable_button(name):
    window.FindElement(name).Update(disabled = True)

def enable_button(name):
    try:
        window.FindElement(name).Update(disabled = False)
    except:
        pass

name_to_function = {'Toggle Canvas' : toggle_canvas,
                    'Toggle Force Vectors' : toggle_force_vectors,
                    'Play/Pause' : unfinished,
                    'Change Color' : unfinished}

while True:
    event, values = window.read(timeout = 15)
    envisionMain.update()
    if event == 'Parse':
        try:
            stop_visualisation(envisonMain_equivalent.get(active_vis))
            if active_vis != '':
                enable_button(active_vis)
                active_vis = ''
            if find_selection_parse(values):
                parse_progress_bar(str(find_selection_parse(values)))
                window.FindElement('parse_status').Update('Succesfully parsed: ' + find_selection_parse(values))
                active_dataset = True
            else:
                sg.Popup('Please select a VASP directory to parse', title = 'Warning', keep_on_top=True)
        except:
            pass
    if event in visualisations_t and active_dataset == True:
        if active_vis == '':
            console_message('Showing: ' + event)
            create_vis_attributes(visualisations_d[event])
            disable_button(event)
            try:
                start_visualisation(envisonMain_equivalent[event])

            except:
                console_message('Error in starting visualisation')
            active_vis = event
        elif active_vis != event:
            try:
                stop_visualisation(envisonMain_equivalent.get(active_vis))
            except:
                pass
            console_message('Ending: ' + active_vis)
            enable_button(active_vis)
            console_message('Showing: ' + event)
            create_vis_attributes(visualisations_d[event])
            disable_button(event)
            try:
                start_visualisation(envisonMain_equivalent[event])

            except:
                console_message('Error in starting visualisation')
            active_vis = event

        else:
            continue
    if event in attr_keys:
        name_to_function[window.FindElement(event).get_text()](envisonMain_equivalent.get(active_vis))
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

window.close()

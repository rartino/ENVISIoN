import sys, os, inspect
import time
import select
import json
import random as rd
import PySimpleGUI as sg
os.popen('export INVIWO_HOME="$HOME/ENVISIoN/inviwo-build/bin"')
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
from envisionpy.EnvisionMain import EnvisionMain
import envisionpy
from envisionpy.hdf5parser import *
import threading
import queue

def send_request(rtype, data):
    return envisionMain.handle_request({'type': rtype, 'parameters': data})

sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.devnull, "w")

canvas = True
vectors = True
back_color = 'lightblue'
t_color = 'black'

envisionMain = EnvisionMain()

parsers = {path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/NaCl_charge_density" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.charge, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/Cu_band_CUB": [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.charge, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/CuFeS2_band_CBT2": [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.charge, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/partial_charges" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.charge, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/TiO2_band_TET" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.charge, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/TiPO4_DoS" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.dos, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/TiPO4_ELF" : [envisionpy.hdf5parser.force_parser, envisionpy.hdf5parser.elf, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/MD/VASP/Al_300K" : [envisionpy.hdf5parser.mol_dynamic_parser, envisionpy.hdf5parser.unitcell],
           path_to_current_folder + "/../unit_testing/resources/FCC-Cu" : [envisionpy.hdf5parser.fermi_parser]}

parsers_vises = {'All' : ['Force', 'Charge', 'MolecularDynamics', 'AtomPositions', 'ELF', 'Dos', 'FermiVolume'],
                 path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure" : ['Force', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/NaCl_charge_density" : ['Force', 'Charge', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/Cu_band_CUB": ['Force', 'Charge', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/CuFeS2_band_CBT2": ['Force', 'Charge', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/partial_charges" : ['Force', 'Charge', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/TiO2_band_TET" : ['Force', 'Charge', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/TiPO4_DoS" : ['Force', 'Dos', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/TiPO4_ELF" : ['Force', 'ELF', 'AtomPositions'],
                 path_to_current_folder + "/../unit_testing/resources/FCC-Cu" : ['FermiVolume'],
                 path_to_current_folder + "/../unit_testing/resources/MD/VASP/Al_300K" : ['MolecularDynamics', 'AtomPositions']}

filenames  = {envisionpy.hdf5parser.force_parser : 'Force',
              envisionpy.hdf5parser.charge : 'Charge',
              envisionpy.hdf5parser.dos : 'Dos',
              envisionpy.hdf5parser.elf : 'ELF',
              envisionpy.hdf5parser.fermi_parser : 'FermiVolume',
              envisionpy.hdf5parser.mol_dynamic_parser : 'MolecularDynamics',
              envisionpy.hdf5parser.unitcell : 'AtomPositions'}

force_attr = ['Toggle Canvas',
              'Toggle Force Vectors']

moldyn_attr = ['Toggle Canvas',
               'Play/Pause',
               'Change Color']

atom_attr = ['Toggle Canvas']

charge_attr = ['Toggle Canvas']

elf_attr = ['Toggle Canvas']

band_attr = ['Toggle Canvas']

dos_attr = ['Toggle Canvas']

fermi_attr = ['Toggle Canvas']

visualisations = ['Force',
                 'MolecularDynamics',
                 'AtomPositions',
                 'Charge',
                 'ELF',
                 'Dos',
                 'FermiVolume']

vasp_directory = [i.rsplit('/', 1)[-1] for i in list(parsers.keys())]

vasp_paths = [i for i in list(parsers.keys())]

visualisations_t = tuple(visualisations)

visualisations_d = {'Force' : force_attr,
                    'MolecularDynamics' : moldyn_attr,
                    'AtomPositions' : atom_attr,
                    'Charge' : charge_attr,
                    'ELF' : elf_attr,
                    'Dos' : dos_attr,
                    'FermiVolume' : fermi_attr}

envisonMain_equivalent = {'Force' : 'force',
                          'MolecularDynamics' : 'molecular_dynamics',
                          'AtomPositions' : 'atom',
                          'Charge' : 'charge',
                          'ELF' : 'elf',
                          'Dos' : 'dos',
                          'FermiVolume' : 'fermi'}

attr = ['Toggle Canvas',
        'Toggle Force Vectors',
        'Play/Pause',
        'Change Color']

attr_keys = ('opt0', 'opt1', 'opt2', 'opt3')

layout = [

    [[sg.Text('ENVISIoN GUI v0.0.0.2', background_color = back_color, justification = 'center', text_color = t_color, font = ("Helvetica", 40, 'bold'))]],
    [[sg.Text('Choose the preferred VASP directory:', background_color = back_color, text_color = t_color, font = ("Helvetica", 14, 'bold'))]],
    [[sg.Radio(vasp_directory[i], 'VASP', enable_events=True, key=vasp_paths[i], background_color = back_color, text_color = t_color)] for i in range(len(vasp_paths))],
    [[sg.Button('Parse', button_color = 'green')]],
    [[sg.Text(text = ' '*80 + '\n' + ' '*80 + '\n' + ' '*80, key = 'parse_status', background_color = back_color, text_color = t_color)]],
    [[sg.Text('Choose what you want to visualize:', background_color = back_color, text_color = t_color, font = ("Helvetica", 14, 'bold'))]],
    [[sg.Button('Force'), sg.Button('MolecularDynamics'), sg.Button('AtomPositions'), sg.Button('Charge')]],
    [[sg.Button('ELF'), sg.Button('Dos'), sg.Button('FermiVolume')]],
    [[sg.Text('Options:', background_color = back_color, text_color = t_color, font = ("Helvetica", 14, 'bold'))]],
    [[sg.Button('1', key = 'opt0', visible = False), sg.Button('2', key = 'opt1', visible = False), sg.Button('3', key = 'opt2', visible = False), sg.Button('4', key = 'opt3', visible = False)]],
    [[sg.Button('Exit', button_color = 'red')]],
    [[sg.Text(text = ' '*80 + '\n' + ' '*80 + '\n' + ' '*80, background_color = back_color, text_color = t_color)]],
    [[sg.Multiline(default_text='Welcome to GUI Numero Dos', key = 'textbox',size=(35, 6), no_scrollbar = True, autoscroll = True, write_only = True),
      sg.Text('Remember to unzip files in the \nAl_300K directory before parsing' ,background_color = back_color, text_color = t_color, font = ("Helvetica", 14, 'bold'))]]

    ]

window = sg.Window('GUI',layout, background_color = back_color, icon = 'Graphics/logotyp.png')
active_dataset = False
active_vis = ''

def delete_prior_hdf5():
    try:
        test = os.listdir(path_to_current_folder + '/../')
        for item in test:
            if item.endswith(".hdf5"):
                os.remove(os.path.join(path_to_current_folder + '/../',item))
        return True
    except:
        print('Couldnt remove')

def parse(vasp_path):
    if delete_prior_hdf5():
        try:
            for key, values in parsers.items():
                if key == vasp_path:
                    for value in values:
                        value(path_to_current_folder + '/../' + filenames[value] + '.hdf5', vasp_path)
            toggle_avaible_visualisations(vasp_path)
            console_message('Succesfully parsed the chosen directory')
        except:
            console_message('Be patient')
            parse(vasp_path)


def toggle_canvas(file, type):
    global canvas
    try:
        if canvas:
            envisionMain.update()
            send_request('visualisation_request', [file, type, "hide", []])
            envisionMain.update()
            canvas = False
        else:
            envisionMain.update()
            send_request('visualisation_request', [file, type, "show", []])
            envisionMain.update()
            canvas = True
        console_message('Canvas Toggled')
    except:
        console_message('Failed to toggle Canvas')
    return

def toggle_force_vectors(file, type):
    global vectors
    try:
        if type == 'force':
            if vectors:
                envisionMain.update()
                send_request("visualisation_request", [file, type, "hide_vectors"])
                envisionMain.update()
                vectors = False
            else:
                envisionMain.update()
                send_request("visualisation_request", [file, type, "show_vectors"])
                envisionMain.update()
                vectors = True
        else:
            console_message('Failed to toggle Vectors')
        console_message('Vectors Toggled')
    except:
        pass
    return

def unfinished(file, type):
    console_message('Not yet implemented')
    return

def console_message(msg):
    window['textbox'].Update('\n' + msg, append = True)
    return

def start_visualisation(file, type):
    envisionMain.update()
    send_request('init_manager', [path_to_current_folder + '/../' + file + '.hdf5'])
    envisionMain.update()
    send_request('start_visualisation', [file, type])
    envisionMain.update()

def stop_visualisation(file, type):
    try:
        envisionMain.update()
        send_request('stop_visualisation', [file, type])
        envisionMain.update()
    except:
        console_message('Could not find active visualisation to terminate')

def find_selection_parse(values):
    for key, value in values.items():
        if value:
            return key
    return False

def toggle_avaible_visualisations(vasp_path):
    for i in parsers_vises['All']:
        if i in parsers_vises[vasp_path]:
            window.FindElement(i).Update(visible = True, button_color = 'green', disabled = False)
        else:
            window.FindElement(i).Update(visible = True, button_color = 'lightgrey', disabled = True)

def create_vis_attributes(attr):
    for i in range(len(attr)):
        window.FindElement('opt' + str(i)).Update(text = attr[i], visible = True, button_color = 'green')
    p = len(attr)
    while p < 4:
        window.FindElement('opt' + str(p)).Update(visible = False, button_color = 'green')
        p += 1
    return

def parse_progress_bar(vasp_path):
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
            parse(vasp_path)
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

    event, values = window.read(timeout = 10) #Timeout inversely sets framerate
    envisionMain.update()                     #Update envisionMain when we draw a new frame
    if event == 'Parse':
        try:
            stop_visualisation(active_vis, envisonMain_equivalent.get(active_vis))
            if active_vis != '':
                enable_button(active_vis)
                active_vis = ''
            if find_selection_parse(values):
                parse_progress_bar(str(find_selection_parse(values)))
                window.FindElement('parse_status').Update('Succesfully parsed: ' +
                                                          find_selection_parse(values))
                active_dataset = True
            else:
                sg.Popup('Please select a VASP directory to parse',
                         title = 'Warning', keep_on_top=True)
        except:
            pass
    if event in visualisations_t and active_dataset == True:
        if active_vis == '':
            console_message('Starting: ' + event)
            create_vis_attributes(visualisations_d[event])
            disable_button(event)
            #try:
            start_visualisation(event, envisonMain_equivalent[event])
            #except:
                #console_message('Error in starting visualisation, choose something else')
            active_vis = event
        elif active_vis != event:
            try:
                stop_visualisation(active_vis, envisonMain_equivalent.get(active_vis))
            except:
                pass
            console_message('Ending: ' + active_vis)
            enable_button(active_vis)
            console_message('Starting: ' + event)
            create_vis_attributes(visualisations_d[event])
            disable_button(event)
            #try:
            start_visualisation(event, envisonMain_equivalent[event])
            #except:
            #    console_message('Error in starting visualisation, choose something else')
            active_vis = event
        else:
            continue
    if event in attr_keys:
        name_to_function[window.FindElement(event).get_text()](active_vis, envisonMain_equivalent.get(active_vis))
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

window.close()

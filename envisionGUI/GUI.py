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
from yaml import load, dump
#try:
#    from yaml import CLoader as Loader, CDumper as Dumper
#except ImportError:
#    from yaml import Loader, Dumper

def send_request(rtype, data):
    return envisionMain.handle_request({'type': rtype, 'parameters': data})

envisionMain = EnvisionMain()

sg.theme('DarkGrey14')

# ------------------------------------------------------------------------- #
#                         Variables and Globals                             #
# ------------------------------------------------------------------------- #

current_dataset = None
current_folder = None
max_datasets = 5
dataset_dir = {}
dataset_vises = {}

visualisations = {'Force' : 'force',
                  'Molecular Dynamics' : 'moldyn',
                  'PCF' : 'pcf',
                  'BandStructure' : 'band2d',
                  'BandStructure 3D' : 'band3d',
                  'Charge' : 'charge',
                  'ELF' : 'elf',
                  'Fermi Surface' : 'fermi',
                  'Atom Positions' : 'atom'}

# ------------------------------------------------------------------------- #
#                       Functions that set up the GUI                       #
# ------------------------------------------------------------------------- #

def setup_datasets(return_keys = False):
    global dataset_dir, dataset_vises
    if not return_keys:
        for i in range(max_datasets):
            dataset_dir['data' + str(i)] = None
            dataset_vises['data' + str(i)] = None
        return [[sg.Button('Empty Dataset', key = 'data' + str(i),
                           visible = True, size = (18, 3),
                           enable_events = True)]
                 for i in range(max_datasets)]
    else:
        return tuple('data' + str(i) for i in range(max_datasets))

def setup_folderloader(return_key = False):
    if not return_key:
        return [[sg.FolderBrowse(button_text = 'Choose VASP-directory',
                                 initial_folder = path_to_current_folder +
                                 '/../unit_testing/resources',
                                 enable_events = True, key = 'foldload',
                                 size = (18,2))],
                [sg.Text('', visible = False, key = 'foldloadtext',
                         size = (18,2))],
                [sg.Button('Parse Selected \n Folder', size = (18,2),
                           enable_events = True, key = 'parsefolder')]
                ]

def setup_vis_buttons():
    button_row = []
    temp_row1 = []
    temp_row2 = []
    half_vis = round(len(visualisations)/2)
    vis_first_half = list(visualisations.keys())[:half_vis]
    vis_last_half = list(visualisations.keys())[half_vis:]
    for i in vis_first_half:
        temp_row1.append(sg.Button(i))
    for i in vis_last_half:
        temp_row2.append(sg.Button(i))
    button_row.append(temp_row1)
    button_row.append(temp_row2)
    return button_row

def get_selected_dataset():
    return current_dataset

def set_selected_dataset(event):
    global current_dataset
    for i in list(setup_datasets(True)):
        if i == event:
            window.FindElement(i).Update(visible = True,
                                         button_color = 'green')
            current_dataset = i
        else:
            window.FindElement(i).Update(visible = True,
                                         button_color = ("#fafbfc", "#155398"))

def set_dataset_to_vises_and_dir(vasp_path = None, current_visualisations = None):
    global dataset_dir, dataset_vises, visualisations, current_dataset
    dataset_dir[current_dataset] = vasp_path
    dataset_vises[current_dataset] = current_visualisations
    window.FindElement(current_dataset).Update(current_folder.rsplit('/', 1)[-1])
    for key, value in visualisations.items():
        if key in dataset_vises[current_dataset]:
            window.FindElement(key).Update(disabled = False, button_color = 'green')
        else:
            window.FindElement(key).Update(disabled = True, button_color = 'lightgrey')



def switch_dataset(event):
    global dataset_dir, dataset_vises
    if dataset_dir[event] != None and dataset_vises[event] != None:
        for key, value in visualisations.items():
            if key in dataset_vises[event]:
                window.FindElement(key).Update(disabled = False, button_color = 'green')
            else:
                window.FindElement(key).Update(disabled = True, button_color = 'lightgrey')
    elif dataset_dir[event] == None:
        for key in visualisations.keys():
            window.FindElement(key).Update(disabled = True, button_color = 'lightgrey')
    else:
        pass

def get_selected_folder():
    return current_folder

def set_selected_folder(values):
    global current_folder
    current_folder = values['foldload']
    window.FindElement('foldloadtext').Update('Currently Selected: \n' +
    current_folder.rsplit('/', 1)[-1], visible = True)

def get_loaded_datasets():
    return tuple([i for i in dataset_dir.values() if i != None])


# ------------------------------------------------------------------------- #
#                        Parsing related functions                          #
# ------------------------------------------------------------------------- #

def parse(vasp_path, current_dataset):
    clear_hdf5(current_dataset)
    pos_vises = []
    if envisionpy.hdf5parser.check_directory_force_parser(vasp_path):
        pos_vises.append('Force')
        envisionpy.hdf5parser.force_parser('force' + current_dataset + '.hdf5', vasp_path)
    # Följt av if satser för alla parsers.
    set_dataset_to_vises_and_dir(vasp_path, pos_vises)

def clear_hdf5(current_dataset):
    try:
        test = os.listdir(path_to_current_folder + '/../envisionGUI/')
        print(test)
        for item in test:
            if item.endswith(current_dataset + ".hdf5"):
                os.remove(os.path.join(path_to_current_folder + '/../envisionGUI',item))
        return True
    except:
        print('Couldnt remove')


# ------------------------------------------------------------------------- #
#            Functions that control the look of visualisations              #
# ------------------------------------------------------------------------- #

def toggle_canvas(file, type):
    global canvas
    #try:
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
        #console_message('Canvas Toggled')
    #except:
        #console_message('Failed to toggle Canvas')
    return

def set_shading_mode(file, type, key):
    try:
       send_request("visualisation_request",
                    [file, type, "set_shading_mode", [key]])
    except:
       console_message('Could not set shading mode')

def set_color(file, type, key):
    try:
       send_request("visualisation_request",
                    [file, type, "set_color", [colors[key]]])
    except:
       console_message('Could not set color')

def set_volume_selection(file, type, key):
    try:
       send_request("visualisation_request", [file, type,
                    "set_volume_selection", [key]])
    except:
       console_message('Could not set volume selection')

def toggle_force_vectors(file, type):
    global vectors
    try:
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
        console_message('Vectors Toggled')
    except:
        console_message('Failed to toggle Vectors')
    return

def toggle_iso_surface(file, type):
    global toggle_iso
    try:
        if toggle_iso:
            envisionMain.update()
            send_request("visualisation_request", [file, type, 'toggle_iso',
                         [toggle_iso]])
            envisionMain.update()
            toggle_iso = False
        else:
            envisionMain.update()
            send_request("visualisation_request", [file, type, 'toggle_iso',
                         [toggle_iso]])
            envisionMain.update()
            toggle_iso = True
        console_message('ISO Toggled')
    except:
        console_message('Failed to toggle ISO')
    return

def set_iso_surface(file, type, value):
    try:
        send_request("visualisation_request", [file, type, "set_iso_surface",
                     [value]])
    except:
        console_message('Could not set ISO-surface value')

def set_radius(file, type, value):
    try:
        send_request("visualisation_request", [file, type, "set_radius",
                     [value]])
    except:
        console_message('Could not set radius')

def toggle_slice_canvas(file, type):
    global slice_canvas
    try:
        if slice_canvas:
            envisionMain.update()
            send_request('visualisation_request', [file, type, "hide",
                         [False, True]])
            envisionMain.update()
            slice_canvas = False
        else:
            envisionMain.update()
            send_request('visualisation_request', [file, type, "show",
                         [False, True]])
            envisionMain.update()
            slice_canvas = True
        console_message('Slice Canvas Toggled')
    except:
        console_message('Failed to toggle Slice Canvas')
    return

def toggle_slice_plane(file, type):
    global slice_plane
    try:
        if slice_plane:
            envisionMain.update()
            send_request("visualisation_request", [file, type,
                         'toggle_slice_plane', [slice_plane]])
            envisionMain.update()
            slice_plane = False
        else:
            envisionMain.update()
            send_request("visualisation_request", [file, type,
                         'toggle_slice_plane', [slice_plane]])
            envisionMain.update()
            slice_plane = True
        console_message('Slice Plane Toggled')
    except:
        console_message('Failed to toggle Slice Plane')
    return

def set_slice_plane_height(file, type, value):
    try:
        send_request("visualisation_request", [file, type,
                     "set_plane_height", [value]])
    except:
        console_message('Could not set slice plane height')

def unfinished(file, type):
    console_message('Not yet implemented')
    return

def set_animation_speed(file, type, speed):
    speed = round(-3.7647 + 103.7647*2.7182**(-3.3164*speed))
    try:
        send_request("visualisation_request", [file, type, "set_speed",
                     [speed]])
    except:
        console_message('Could not set speed')

def set_opacity(file, type, value):
    try:
        send_request("visualisation_request", [file, type, "set_opacity",
                     [value]])
    except:
        console_message('Could not set opacity')

def play_pause(file, type):
    try:
        send_request("visualisation_request", [file, type, "play_pause"])
    except:
        console_message('Could not set play/pause')

def set_standard_parameters(file, type):
    try:
        set_radius(file, type, 0.5)
    except:
        pass
    try:
        set_animation_speed(file, type, 0.5)
    except:
        pass
    try:
        set_opacity(file, type, 1)
    except:
        pass

# ------------------------------------------------------------------------- #
#                             Layout Settings                               #
# ------------------------------------------------------------------------- #

layout = [[sg.Frame(layout = setup_datasets(), title = ''),
           sg.Frame(layout = setup_folderloader(), title = '',
           vertical_alignment = 'bottom')],
          [sg.Frame(layout = setup_vis_buttons(), title = '')]]


window = sg.Window('',layout)

# ------------------------------------------------------------------------- #
#                               Event Loop                                  #
# ------------------------------------------------------------------------- #

while True:
    envisionMain.update()
    event, values = window.read(timeout = 10)
    if event == 'foldload':
        set_selected_folder(values)

    if (event == 'parsefolder' and current_folder != None
                               and current_folder not in get_loaded_datasets()
                               and current_dataset != None):
        parse(current_folder, current_dataset)
    if event in setup_datasets(True):
        set_selected_dataset(event)
        switch_dataset(event)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
window.close()

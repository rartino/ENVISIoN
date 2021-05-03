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

allow_simultaneous_visualisations = True
allow_simultaneous_visualisations_over_datasets = True
current_dataset = None
current_folder = None
number_of_buttons = 4
number_of_sliders = 4
number_of_comboboxes = 4
max_datasets = 5
dataset_dir = {}
dataset_vises = {}
active_vises = {}

visualisations = {'Force' : 'force',
                  'Molecular Dynamics' : 'moldyn',
                  'PCF' : 'pcf',
                  'BandStructure' : 'band2d',
                  'BandStructure 3D' : 'band3d',
                  'Charge' : 'charge',
                  'ELF' : 'elf',
                  'Fermi Surface' : 'fermi',
                  'Atom Positions' : 'atom'}

visualisations_button_tuple = tuple([i for i in visualisations.keys()])

force_attr = {'button0' : 'Toggle Canvas',
              'button1' : 'Toggle Force Vectors',
              'slider': {'Set Radius': [(0,100), 50]}}

moldyn_atttr = {'button0' : 'Toggle Canvas',
                'button1' : 'Play/Pause',
                'slider': {'Set Radius': [(0,100), 50],
                           'Set Speed': [(0,100), 50],
                           'Set Opacity': [(0,100), 100]}}

pcf_attr = {'button0' : 'Toggle Canvas'}

band2d_attr = {'button0' : 'Toggle Canvas'}

band3d_attr = {'button0' : 'Toggle Canvas'}

volume_attr = {'button0' : 'Toggle Canvas',
               'button1' : 'Toggle ISO',
               'button2' : 'Toggle Slice Canvas',
               'button3' : 'Toggle Slice Plane',
               'combo' : {'Shading Mode' : ['No Shading', 'Ambient', 'Diffuse',
                                            'Specular', 'Blinn Phong', 'Phong'],
                          'Volume Selection' : ['/0', '/1', '/final']},
               'slider': {'ISO Surface Value': [(0,100), 50],
                          'Slice Plane Height': [(0,100), 50]}}

atom_attr = {'button0' : 'Toggle Canvas'}

vis_attributes = {'Force' : force_attr,
                  'Molecular Dynamics' : moldyn_atttr,
                  'PCF' : pcf_attr,
                  'BandStructure' : band2d_attr,
                  'BandStructure 3D' : band3d_attr,
                  'Charge' : volume_attr,
                  'ELF' : volume_attr,
                  'Fermi Surface' : volume_attr,
                  'Atom Positions' : atom_attr}

# ------------------------------------------------------------------------- #
#                       Functions that set up the GUI                       #
# ------------------------------------------------------------------------- #
def setup_option_buttons(return_keys = False):
    if not return_keys:
        return [[sg.Button(i, key = 'opt' + str(i), visible = False)]
                 for i in range(number_of_buttons)]
    else:
        return tuple('opt' + str(i) for i in range(number_of_buttons))

def setup_combo_boxes(return_keys = False):
    if not return_keys:
        combo_row = []
        for i in range(number_of_comboboxes):
            combo_row.append([sg.Text('Combo' + str(i), key = 'com' + \
                                      str(i) + 't',
                                      visible = False, size = (18, 1))])
            combo_row.append([sg.Combo([str(i)], key = 'com' + str(i),
                                       visible = False,
                                       readonly = True, enable_events = True)])
        return combo_row
    else:
        return tuple('com' + str(i) for i in range(number_of_comboboxes))

def setup_sliders(return_keys = False):
    if not return_keys:
        slider_row = []
        for i in range(number_of_sliders):
            slider_row.append([sg.Slider(range = (0, 100), key = 'sli' + str(i),
                                         visible = False,
                                         orientation = 'horizontal',
                                         resolution = 5,
                                         default_value = 50, size = (15,20),
                                         enable_events = True,
                                         disable_number_display = True)])
            slider_row.append([sg.Text('Slider' + str(i), key = 'sli' + str(i) + \
                                       't', visible = False,
                     size = (30,2))])
        return slider_row
    else:
        return tuple('sli' + str(i) for i in range(number_of_sliders))

def setup_datasets(return_keys = False):
    global dataset_dir, dataset_vises, active_vises
    if not return_keys:
        for i in range(max_datasets):
            dataset_dir['data' + str(i)] = None
            dataset_vises['data' + str(i)] = None
            active_vises['data' + str(i)] = []
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
    print(current_folder)
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

def clear_hdf5(current_dataset, exit = False):
    if not exit:
        try:
            test = os.listdir(path_to_current_folder + '/../envisionGUI/')
            print(test)
            for item in test:
                if item.endswith(current_dataset + ".hdf5"):
                    os.remove(os.path.join(path_to_current_folder + '/../envisionGUI',item))
            return True
        except:
            print('Couldnt remove')
    else:
        try:
            test = os.listdir(path_to_current_folder + '/../envisionGUI/')
            print(test)
            for item in test:
                if item.endswith(".hdf5"):
                    os.remove(os.path.join(path_to_current_folder + '/../envisionGUI',item))
            return True
        except:
            print('Couldnt remove')





def clear_options():
    b=0
    c=0
    s=0
    while b < number_of_buttons:
        window.FindElement('opt' + str(b)).Update(visible = False,
                           button_color = 'green')
        b += 1
    while c < number_of_comboboxes:
        window.FindElement('com' + str(c)).Update(visible = False)
        window.FindElement('com' + str(c) + 't').Update(visible = False)
        c += 1
    while s < number_of_sliders:
        window.FindElement('sli' + str(s) + 't').Update(visible = False)
        window.FindElement('sli' + str(s)).Update(visible = False)
        s += 1
    return True

# ------------------------------------------------------------------------- #
#               Functions that control the visualisations                   #
# ------------------------------------------------------------------------- #

def handle_visualisation_request(event, current_dataset):
    hdf5_file = visualisations[event] + current_dataset + '.hdf5'
    hdf5_file_name = visualisations[event] + current_dataset
    print(active_vises[current_dataset])
    if event in tuple(active_vises[current_dataset]):
        try:
            stop_visualisation(hdf5_file_name, visualisations[event])
            active_vises[current_dataset].remove(event)
        except:
            pass
    else:
        start_visualisation(hdf5_file_name, hdf5_file, visualisations[event])
        active_vises[current_dataset].append(event)
    print(active_vises[current_dataset])
    print(hdf5_file)

def start_visualisation(filename, file, type):
    envisionMain.update()
    send_request('init_manager', [file])
    envisionMain.update()
    send_request('start_visualisation', [filename, type])
    envisionMain.update()

def stop_visualisation(filename, type):
    try:
        envisionMain.update()
        send_request('stop_visualisation', [filename, type])
        envisionMain.update()
    except:
        pass

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

layout = [[ sg.Frame(layout = setup_datasets(), title = ''),
            sg.Frame(layout = setup_folderloader(), title = '',
            vertical_alignment = 'bottom')],
          [ sg.Frame(layout = setup_vis_buttons(), title = '')],
          [[sg.Frame(layout = setup_option_buttons(), title = ''),
            sg.Frame(layout = setup_sliders(), title = ''),
            sg.Frame(layout = setup_combo_boxes(), title = '')]],
          [ sg.Button('Test', key = 't')]]


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
    if (event in visualisations_button_tuple and current_folder != None
                                            and current_dataset != None):
        handle_visualisation_request(event, current_dataset)
    if event == 't':
        print(dataset_dir)
        print(dataset_vises)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        clear_hdf5(current_dataset, True)
        break
window.close()

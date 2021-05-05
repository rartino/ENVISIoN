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

envisionMain = EnvisionMain()

sg.theme('DarkGrey14')

# ------------------------------------------------------------------------- #
#                         Variables and Globals                             #
# ------------------------------------------------------------------------- #

allow_simultaneous_visualisations = True
allow_simultaneous_visualisations_over_datasets = True
canvas = True
slice_canvas = False
vectors = True
toggle_iso = True
slice_plane = True
current_dataset = None
current_dataset_is_hdf5 = None
current_folder = None
current_file = None
current_vis = None
current_vis_key = None
current_vis_hdf5 = None
number_of_buttons = 4
number_of_sliders = 4
number_of_comboboxes = 4
max_datasets = 5
dataset_dir = {}
dataset_vises = {}
dataset_if_hdf5 = {}
current_vises = {}

visualisations = {'Force' : 'force',
                  'Molecular Dynamics' : 'molecular_dynamics',
                  'PCF' : 'pcf',
                  'BandStructure' : 'band2d',
                  'BandStructure 3D' : 'band3d',
                  'Charge' : 'charge',
                  'ELF' : 'elf',
                  'Fermi Surface' : 'fermi',
                  'Atom Positions' : 'atom'}

visualisations_reverse = {'force' : 'Force',
                  'molecular_dynamics' : 'Molecular Dynamics',
                  'pcf' : 'PCF',
                  'band2d' : 'BandStructure',
                  'band3d' : 'BandStructure 3D',
                  'charge' : 'Charge',
                  'elf' : 'ELF',
                  'fermi' : 'Fermi Surface',
                  'atom' : 'Atom Positions'}

visualisations_button_tuple = tuple([i for i in visualisations.keys()])

force_attr = {'button0' : 'Toggle Canvas',
              'button1' : 'Toggle Force Vectors',
              'slider': {'Set Radius': [(0,100), 50],
                         'Set Opacity': [(0,100), 100]}}

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
    global dataset_dir, dataset_vises, current_vises
    if not return_keys:
        for i in range(max_datasets):
            dataset_dir['data' + str(i)] = None
            dataset_vises['data' + str(i)] = None
            current_vises['data' + str(i)] = []
            dataset_if_hdf5['data' + str(i)] = None
        return [[sg.Button('Empty Dataset', key = 'data' + str(i),
                           visible = True, size = (18, 3),
                           enable_events = True, button_color = 'darkgrey')]
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
                         size = (18,3))],
                [sg.Button('Parse Selected \n Folder', size = (18,2),
                           enable_events = True, key = 'parsefolder')]
                ]

def setup_fileloader(return_key = False):
    if not return_key:
        return [[sg.Text('Note: Loading HDF5-files\ndirectly is not\nwell supported', visible = True, key = 'text',
                 size = (18,4))],
                [sg.FileBrowse(button_text = 'Choose a HDF5-file',
                                 initial_folder = path_to_current_folder + '/../ENVISIoN',
                                 enable_events = True, key = 'fileload',
                                 size = (18,2), file_types = (('*.hdf5', '.hdf5'),))],
                [sg.Text('', visible = False, key = 'fileloadtext',
                         size = (18,3))],
                [sg.Button('Load selected file \nin to dataset', size = (18,2),
                           enable_events = True, key = 'loadfile')]
                ]

def setup_vis_buttons():
    button_row = []
    temp_row1 = []
    temp_row2 = []
    half_vis = round(len(visualisations)/2)
    vis_first_half = list(visualisations.keys())[:half_vis]
    vis_last_half = list(visualisations.keys())[half_vis:]
    for i in vis_first_half:
        temp_row1.append(sg.Button(i, button_color = 'lightgrey', disabled = True))
    for i in vis_last_half:
        temp_row2.append(sg.Button(i, button_color = 'lightgrey', disabled = True))
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
                                         button_color = ("#fafbfc", "darkgrey"))

def set_dataset_to_vises_and_dir(vasp_path = None, current_visualisations = None, hdf5 = False):
    global dataset_dir, dataset_vises, visualisations, current_dataset, current_dataset_is_hdf5
    dataset_dir[current_dataset] = vasp_path
    dataset_vises[current_dataset] = current_visualisations
    if hdf5:
        dataset_if_hdf5[current_dataset] = current_file
        window.FindElement(current_dataset).Update(current_file.rsplit('/', 1)[-1])
    else:
        dataset_if_hdf5[current_dataset] = None
        window.FindElement(current_dataset).Update(current_folder.rsplit('/', 1)[-1])
    for key, value in visualisations.items():
        if key in dataset_vises[current_dataset]:
            window.FindElement(key).Update(disabled = False, button_color = 'green')
        else:
            window.FindElement(key).Update(disabled = True, button_color = 'lightgrey')

def console_message(str):
    pass


# ------------------------------------------------------------------------- #
#                        Parsing related functions                          #
# ------------------------------------------------------------------------- #

def parse(vasp_path, current_dataset):
    clear_hdf5(current_dataset)
    pos_vises = []
    if envisionpy.hdf5parser.check_directory_force_parser(vasp_path):
        pos_vises.append('Force')
        envisionpy.hdf5parser.force_parser('force' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_molecular_dynamics_parser(vasp_path):
        pos_vises.append('Molecular Dynamics')
        envisionpy.hdf5parser.mol_dynamic_parser('molecular_dynamics' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_elf(vasp_path):
        pos_vises.append('ELF')
        envisionpy.hdf5parser.elf('elf' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_charge(vasp_path):
        if envisionpy.hdf5parser.check_directory_unitcell(vasp_path):
            pos_vises.append('Charge')
            envisionpy.hdf5parser.charge('charge' + current_dataset + '.hdf5', vasp_path)
            envisionpy.hdf5parser.unitcell('charge' + current_dataset + '.hdf5', vasp_path)
        else:
            pos_vises.append('Charge')
            envisionpy.hdf5parser.charge('charge' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_unitcell(vasp_path):
        pos_vises.append('Atom Positions')
        envisionpy.hdf5parser.unitcell('atom' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_bandstructure(vasp_path):
        pos_vises.append('BandStructure')
        envisionpy.hdf5parser.bandstructure('band2d' + current_dataset + '.hdf5', vasp_path)
        pos_vises.append('BandStructure 3D')
        envisionpy.hdf5parser.bandstructure('band3d' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_fermi(vasp_path):
        pos_vises.append('Fermi Surface')
        envisionpy.hdf5parser.fermi_parser('fermi' + current_dataset + '.hdf5', vasp_path)
    if envisionpy.hdf5parser.check_directory_pcf(vasp_path):
        pos_vises.append('PCF')
        envisionpy.hdf5parser.paircorrelation('pcf' + current_dataset + '.hdf5', vasp_path)
    # Följt av if satser för alla parsers.
    set_dataset_to_vises_and_dir(vasp_path, pos_vises)

def parse_progress_bar(vasp_path, current_dataset):
    stop1 = rd.randint(10,30)
    stop2 = rd.randint(40,60)
    stop3 = rd.randint(70,90)
    lenght = 100
    layout = [[sg.Text('Working on it')],
          [sg.ProgressBar(lenght, orientation='h', size=(20, 20),
                          key='progressbar')],
          [sg.Cancel()]]
    window2 = sg.Window('', layout)
    progress_bar = window2['progressbar']
    for i in range(lenght):
        event, values = window2.read(timeout=10)
        if i == stop1:
            time.sleep(0.2)
        if i == stop2:
            parse(vasp_path, current_dataset)
        if i == stop3:
            time.sleep(0.3)
        if event == 'Cancel'  or event == sg.WIN_CLOSED:
            break
        progress_bar.UpdateBar(i + 1)
    window2.close()
    return True

def load_hdf5_file(hdf5_path, current_dataset):
    init = send_request('init_manager', [hdf5_path])
    init = init['data'][2]
    print(hdf5_path)
    envisionMain.update()
    pos_vises = []
    for key, value in visualisations.items():
        if value in init:
            pos_vises.append(key)
    set_dataset_to_vises_and_dir(hdf5_path, pos_vises, True)
    print(pos_vises)

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
def create_vis_attributes(attr):
    clear_options()
    button_count = 0
    combo_count = 0
    slider_count = 0
    for key, value in attr.items():
        if 'button' in key:
            window.FindElement('opt' +
                               str(button_count)).Update(text = value,
                               visible = True, button_color = 'green')
            button_count += 1
        elif 'combo' in key:
            for key1, value1 in value.items():
                window.FindElement('com' + str(combo_count) +
                                   't').Update(value = key1, visible = True)
                window.FindElement('com' +
                                   str(combo_count)).Update(values = value1,
                                   visible = True)
                combo_count += 1
        elif 'slider' in key:
            for key2, value2 in value.items():
                window.FindElement('sli' + str(slider_count) +
                                   't').Update(value = key2 + ': ' +
                                   str(value2[1]/100), visible = True)
                window.FindElement('sli' +
                                   str(slider_count)).Update(range = value2[0],
                                   value = value2[1], visible = True,
                                   disabled = False)
                slider_count += 1
    return

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

def set_selected_file(values):
    global current_file
    current_file = values['fileload']
    window.FindElement('fileloadtext').Update('Currently Selected: \n' +
    current_file.rsplit('/', 1)[-1], visible = True)

def get_loaded_datasets():
    return tuple([i for i in dataset_dir.values() if i != None])

def handle_visualisation_request(event, current_dataset, hdf5 = False):
    if dataset_if_hdf5[current_dataset] == None:
        hdf5_file = visualisations[event] + current_dataset + '.hdf5'
        hdf5_file_name = visualisations[event] + current_dataset
    else:
        hdf5_file = dataset_if_hdf5[current_dataset]
        hdf5_file_name = dataset_if_hdf5[current_dataset].rsplit('.hdf5')[0]
        hdf5_file_name = hdf5_file_name.rsplit('/', 1)[-1]
        print()
    if event not in current_vises[current_dataset]:
        print(current_vises[current_dataset])
        print(hdf5_file_name + ' ' + hdf5_file + ' ' + visualisations[event])
        start_visualisation(hdf5_file_name, hdf5_file, visualisations[event])
        current_vises[current_dataset].append(event)
    print(current_vises[current_dataset])
    print(hdf5_file)

def start_visualisation(filename, file, type):
    envisionMain.update()
    send_request('init_manager', [file])
    envisionMain.update()
    print(filename)
    print(type)
    send_request('start_visualisation', [filename, type])
    envisionMain.update()

def stop_visualisation(filename, type):
    try:

        envisionMain.update()
        send_request('stop_visualisation', [filename, type])
        envisionMain.update()
    except:
        pass

def set_current(event, current_dataset):
    global current_vis_hdf5, current_vis, current_vis_key
    if dataset_if_hdf5[current_dataset] == None:
        current_vis_hdf5 = visualisations[event] + current_dataset
        current_vis = visualisations[event]
        current_vis_key = str([vis for vis,val in visualisations.items() if val == current_vis][0])
    else:
        current_vis_hdf5 = dataset_if_hdf5[current_dataset].rsplit('.hdf5')[0]
        current_vis_hdf5 = current_vis_hdf5.rsplit('/', 1)[-1]
        current_vis = visualisations[event]
        current_vis_key = str([vis for vis,val in visualisations.items() if val == current_vis][0])
def stop_selected(current_vis_hdf5, current_vis):
    try:
        current_vises[current_dataset].remove(str([vis for vis,val in visualisations.items() if val == current_vis][0]))
        stop_visualisation(current_vis_hdf5, current_vis)
    except:
        pass

def set_selected(event):
    window.FindElement(event).Update(button_color = 'darkgreen', disabled = True)

def unset_selected(event):
    window.FindElement(current_vis_key).Update(button_color = 'green', disabled = False)
# ------------------------------------------------------------------------- #
#            Functions that control the look of visualisations              #
# ------------------------------------------------------------------------- #

def toggle_canvas(file, type):
    global canvas
    #try:
    print(file + type)
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
                    [file, type, "set_color", [key]])
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
    try:
        set_color(file, type, [1,1,1])
    except:
        pass

# ------------------------------------------------------------------------- #
#                             Layout Settings                               #
# ------------------------------------------------------------------------- #

layout = [[ sg.Frame(layout = setup_datasets(), title = ''),
            sg.Frame(layout = setup_folderloader(), title = '',
            vertical_alignment = 'bottom'),
            sg.Frame(layout = setup_fileloader(), title = '',
            vertical_alignment = 'bottom'),
            ],
          [ sg.Frame(layout = setup_vis_buttons(), title = '', border_width = 0)],
          [[sg.Frame(layout = setup_option_buttons(), title = '', border_width = 0),
            sg.Frame(layout = setup_sliders(), title = '', border_width = 0),
            sg.Frame(layout = setup_combo_boxes(), title = '', border_width = 0)]],
          [ sg.Button('Stop Currently Selected Visualisation',
            key = 'stop', button_color = 'red'),
            sg.Text('FPS:'),
            sg.Text('             ', key = 'fps'), sg.Button('test', key ='t')]]


window = sg.Window('',layout)

button_to_function = {'Toggle Canvas' : toggle_canvas,
                    'Toggle Force Vectors' : toggle_force_vectors,
                    'Play/Pause' : play_pause,
                    'Change Color' : unfinished,
                    'Toggle ISO' : toggle_iso_surface,
                    'Toggle Slice Canvas' : toggle_slice_canvas,
                    'Toggle Slice Plane' : toggle_slice_plane}

combo_to_function = {'Shading Mode' : set_shading_mode,
                     'Volume Selection' : set_volume_selection,
                     'Color' : set_color}

slider_to_function = {'ISO Surface Value' : set_iso_surface,
                      'Slice Plane Height' : set_slice_plane_height,
                      'Set Radius' : set_radius,
                      'Set Speed' : set_animation_speed,
                      'Set Opacity' : set_opacity}


# ------------------------------------------------------------------------- #
#                               Event Loop                                  #
# ------------------------------------------------------------------------- #

while True:
    start = time.time()
    envisionMain.update()
    event, values = window.read(timeout = 20)
    if event == 'foldload':
        set_selected_folder(values)
    if event == 'fileload':
        set_selected_file(values)
    if (event == 'parsefolder' and current_folder != None
                               and current_folder not in get_loaded_datasets()
                               and current_dataset != None):
        parse_progress_bar(current_folder, current_dataset)
    if (event == 'loadfile' and current_file != None
                            and current_file not in get_loaded_datasets()
                            and current_dataset != None):
        load_hdf5_file(current_file, current_dataset)
    if event in setup_datasets(True):
        set_selected_dataset(event)
        switch_dataset(event)
    if (event in visualisations_button_tuple and (current_folder != None or current_file != None)
                                            and current_dataset != None):
        switch_dataset(current_dataset)
        set_selected(event)
        create_vis_attributes(vis_attributes[event])
        print(event)
        handle_visualisation_request(event, current_dataset)
        set_current(event, current_dataset)
        set_standard_parameters(current_vis_hdf5, current_vis)
    if (event == 'stop' and (current_folder != None or current_file != None)
                                            and current_dataset != None):
        unset_selected(current_vis)
        stop_selected(current_vis_hdf5, current_vis)
        clear_options()
    if event == 't':
        print(current_dataset)
        print(current_vises)

    if event in setup_option_buttons(True):
        button_to_function[window.FindElement(event).get_text()](current_vis_hdf5,
                                                                 current_vis)
    if event in setup_combo_boxes(True):
        combo_to_function[window.FindElement(event + 't').get()](current_vis_hdf5,
                                                                 current_vis, values[event])
    if event in setup_sliders(True):
        window.FindElement(event + 't').Update(value =
                          (window.FindElement(event + 't').get().split(':'))[0]
                          + ': ' + str(round(values[event])/100))
        slider_to_function[window.FindElement(event +
                                        't').get().split(':')[0]](current_vis_hdf5,
                                                                  current_vis, round(values[event])/100)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        clear_hdf5(current_dataset, True)
        break
    end = time.time()
    window.FindElement('fps').Update(str(round(1/(end - start), 1)))
window.close()

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

with open('GUIconfig.yml') as c:
    config = load(c)


''' Suppress unwanted CMD output '''
#sys.stdout = open(os.devnull, "w")
#sys.stderr = open(os.devnull, "w")

''' Setting up necessary data '''
active_dataset = config['VARIABLES']['active_dataset']
active_vis = config['VARIABLES']['active_vis']
canvas = config['VARIABLES']['canvas']
slice_canvas = config['VARIABLES']['slice_canvas']
vectors = config['VARIABLES']['vectors']
toggle_iso = config['VARIABLES']['toggle_iso']
slice_plane = config['VARIABLES']['slice_plane']
number_of_buttons = config['VARIABLES']['number_of_buttons']
number_of_comboboxes = config['VARIABLES']['number_of_comboboxes']
number_of_sliders = config['VARIABLES']['number_of_sliders']
parsers = config['DICTIONARIES']['parsers']
tooltips = config['DICTIONARIES']['tooltips']
force_attr = config['DICTIONARIES']['ATTRIBUTES']['force_attr']
moldyn_attr = config['DICTIONARIES']['ATTRIBUTES']['moldyn_attr']
atom_attr = config['DICTIONARIES']['ATTRIBUTES']['atom_attr']
charge_attr = config['DICTIONARIES']['ATTRIBUTES']['charge_attr']
elf_attr = config['DICTIONARIES']['ATTRIBUTES']['elf_attr']
band_attr = config['DICTIONARIES']['ATTRIBUTES']['band_attr']
band3d_attr = config['DICTIONARIES']['ATTRIBUTES']['band3d_attr']
dos_attr = config['DICTIONARIES']['ATTRIBUTES']['dos_attr']
pcf_attr = config['DICTIONARIES']['ATTRIBUTES']['pcf_attr']
fermi_attr = config['DICTIONARIES']['ATTRIBUTES']['fermi_attr']
band3d_attr = config['DICTIONARIES']['ATTRIBUTES']['band_attr']
visualisations = config['LISTS']['visualisations']
envisionMain_equivalent = config['DICTIONARIES']['envisionMain_equivalent']
filenames  = {envisionpy.hdf5parser.force_parser : 'Force',
              envisionpy.hdf5parser.charge : 'Charge',
              envisionpy.hdf5parser.dos : 'Dos',
              envisionpy.hdf5parser.elf : 'ELF',
              envisionpy.hdf5parser.fermi_parser : 'FermiVolume',
              envisionpy.hdf5parser.mol_dynamic_parser : 'MolecularDynamics',
              envisionpy.hdf5parser.unitcell : 'AtomPositions',
              envisionpy.hdf5parser.paircorrelation : 'PCF',
              envisionpy.hdf5parser.bandstructure_combo3d : 'BandStructure3D',
              envisionpy.hdf5parser.bandstructure_combo : 'BandStructure'
              }

new_keys = []
new_values = []
for key, values in parsers.items():
    new_keys.append('{}{}'.format(path_to_current_folder, key))
    new_value = []
    for value in values:
        new_value.append(list(filenames.keys())[list(filenames.values()).index(value)])
    new_values.append(new_value)
parsers_vises = dict(zip(new_keys, list(parsers.values())))
parsers = dict(zip(new_keys, new_values))
parsers_t = tuple(parsers.keys())
tooltips = [i for i in list(tooltips.values())]
parsers_vises['All'] = [i for i in visualisations]
vasp_directory = [i.rsplit('/', 1)[-1] for i in list(parsers.keys())]
vasp_paths = [i for i in list(parsers.keys())]
visualisations_t = tuple(visualisations)
visualisations_d = {'Force' : force_attr,
                    'MolecularDynamics' : moldyn_attr,
                    'AtomPositions' : atom_attr,
                    'Charge' : charge_attr,
                    'ELF' : elf_attr,
                    'Dos' : dos_attr,
                    'FermiVolume' : fermi_attr,
                    'PCF' : pcf_attr,
                    'BandStructure3D' : band_attr,
                    'BandStructure' : band3d_attr
                    }

''' Layout and interface definitions '''
sg.theme('DarkGrey14')

def setup_radio():
    return [[sg.Radio(vasp_directory[i], 'VASP',
                      font = ("Helvetica", 11, 'bold'),
                      tooltip = tooltips[i], enable_events=True,
                      key=vasp_paths[i])] for i in range(len(vasp_paths))]

vasp_layout = [
              [sg.Text('Choose the preferred VASP directory:',
                       font = ("Helvetica", 14, 'bold'))],
              [sg.Frame(layout = setup_radio(), title = '',	border_width = 0)],
              [sg.Button('Parse', button_color = 'green')],
              [sg.Text(text = ' '*80 + '\n' + ' '*80 + '\n' + ' '*80,
                       key = 'parse_status', visible = False)]
              ]

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

def setup_buttons():
    button_row = []
    temp_row1 = []
    temp_row2 = []
    half_vis = round(len(visualisations)/2)
    vis_first_half = visualisations[:half_vis]
    vis_last_half = visualisations[half_vis:]
    for i in vis_first_half:
        temp_row1.append(sg.Button(i))
    for i in vis_last_half:
        temp_row2.append(sg.Button(i))
    button_row.append(temp_row1)
    button_row.append(temp_row2)
    return button_row


exit_row = [
           [sg.Button('Exit', button_color = 'red')]
           ]

console_row = [
              [sg.Multiline(default_text='Welcome to GUI Numero Dos',
                            key = 'textbox',size=(35, 6), no_scrollbar = True,
                            autoscroll = True, write_only = True),
               sg.Text('Remember to unzip files \nin the Al_300K directory \
                       \nbefore parsing',
                       font = ("Helvetica", 14, 'bold'))]
              ]

layout = [
         [sg.Text('ENVISIoN GUI v0.3', justification = 'center',
                  font = ("Helvetica", 40, 'bold'))],
         [sg.Frame(layout = vasp_layout, title = '', border_width = 0,
                   vertical_alignment = "top")],
         [sg.Frame(layout = setup_buttons(), title = '',border_width = 0,
                   vertical_alignment = "top")],
         [sg.Text('Options:',font = ("Helvetica", 14, 'bold'), key = 'opt_text',
                  visible = False)],
         [sg.Frame(layout = setup_option_buttons(), title = '',
                   border_width = 0,
                   vertical_alignment = "top"),
                   sg.Frame(layout = setup_combo_boxes(), title = '',
                            border_width = 0,
                            vertical_alignment = "top"),
                   sg.Frame(layout = setup_sliders(), title = '',
                            border_width = 0,
                            vertical_alignment = "top")],
         [sg.Frame(layout = console_row, title = '', border_width = 0,
                   vertical_alignment = "top")],
         [sg.Frame(layout = exit_row, title = '', border_width = 0,
                   vertical_alignment = "top")]
         ]

window = sg.Window('',layout, icon = 'Graphics/logotyp.png')

''' Visualisation attribute functions '''
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

''' GUI control functions '''
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
                        value(path_to_current_folder + '/../' +
                              filenames[value] + '.hdf5', vasp_path)
            toggle_avaible_visualisations(vasp_path)
            console_message('Succesfully parsed the chosen directory')
        except:
            console_message('Be patient')
            parse(vasp_path)

def console_message(msg):
    window['textbox'].Update('\n' + msg, append = True)
    return

def start_visualisation(file, type):
    envisionMain.update()
    send_request('init_manager', [path_to_current_folder + '/../' + file +
                 '.hdf5'])
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
            window.FindElement(i).Update(visible = True,
                                         button_color = 'green',
                                         disabled = False)
        else:
            window.FindElement(i).Update(visible = True,
                                         button_color = 'lightgrey',
                                         disabled = True)

def toggle_avaible_visualisations_prior(vasp_path):
    for i in parsers_vises['All']:
        if i in parsers_vises[vasp_path]:
            window.FindElement(i).Update(visible = True,
                                         button_color = 'green',
                                         disabled = True)
        else:
            window.FindElement(i).Update(visible = True,
                                         button_color = 'lightgrey',
                                         disabled = True)

def create_vis_attributes(attr):
    show_opt_text()
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

def show_opt_text():
    window.FindElement('opt_text').Update(visible = True)

def hide_opt_text():
    window.FindElement('opt_text').Update(visible = False)

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

def parse_progress_bar(vasp_path):
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
            hide_opt_text()
            clear_options()
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

''' Name to function dictionaries '''
button_to_function = {'Toggle Canvas' : toggle_canvas,
                    'Toggle Force Vectors' : toggle_force_vectors,
                    'Play/Pause' : unfinished,
                    'Change Color' : unfinished,
                    'Toggle ISO' : toggle_iso_surface,
                    'Toggle Slice Canvas' : toggle_slice_canvas,
                    'Toggle Slice Plane' : toggle_slice_plane}

combo_to_function = {'Shading Mode' : set_shading_mode,
                     'Volume Selection' : set_volume_selection}

slider_to_function = {'ISO Surface Value' : set_iso_surface,
                      'Slice Plane Height' : set_slice_plane_height}

''' GUI event loop '''
while True:
    event, values = window.read(timeout = 10) #Timeout inversely sets framerate
    envisionMain.update()  #Update envisionMain when we draw a new frame
    if event in parsers_t:
        toggle_avaible_visualisations_prior(event)
    if event == 'Parse':
        try:
            stop_visualisation(active_vis,
                               envisionMain_equivalent.get(active_vis))
            if active_vis != '':
                enable_button(active_vis)
                active_vis = ''
            if find_selection_parse(values):
                parse_progress_bar(str(find_selection_parse(values)))
                window.FindElement('parse_status').Update('Succesfully parsed: '
                                                 + find_selection_parse(values))
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
            start_visualisation(event, envisionMain_equivalent[event])
            #except:
                #console_message('Error in starting visualisation, choose something else')
            active_vis = event
        elif active_vis != event:
            try:
                stop_visualisation(active_vis,
                                   envisionMain_equivalent.get(active_vis))
            except:
                pass
            console_message('Ending: ' + active_vis)
            enable_button(active_vis)
            console_message('Starting: ' + event)
            create_vis_attributes(visualisations_d[event])
            disable_button(event)
            #try:
            start_visualisation(event, envisionMain_equivalent[event])
            #except:
            #    console_message('Error in starting visualisation, choose something else')
            active_vis = event
        else:
            continue
    if event in setup_option_buttons(True):
        button_to_function[window.FindElement(event).get_text()](active_vis,
                                         envisionMain_equivalent.get(active_vis))
    if event in setup_combo_boxes(True):
        combo_to_function[window.FindElement(event + 't').get()](active_vis,
                          envisionMain_equivalent.get(active_vis), values[event])
    if event in setup_sliders(True):
        window.FindElement(event + 't').Update(value =
                          (window.FindElement(event + 't').get().split(':'))[0]
                          + ': ' + str(round(values[event])/100))
        slider_to_function[window.FindElement(event +
                                        't').get().split(':')[0]](active_vis,
               envisionMain_equivalent.get(active_vis), round(values[event])/100)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
window.close()

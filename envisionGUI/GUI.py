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

def parse(vasp_path = None):
    num = rd.randint(0,100)
    if num < 50:
        vises = ['Force' , 'BandStructure', 'Molecular Dynamics']
    else:
        vises =  ['PCF', 'ELF', 'Charge']
    set_dataset_to_vises_and_dir(vasp_path, vises)

layout = [[sg.Frame(layout = setup_datasets(), title = ''),
           sg.Frame(layout = setup_folderloader(), title = '', vertical_alignment = 'bottom')],
           [sg.Frame(layout = setup_vis_buttons(), title = '')]]

window = sg.Window('',layout)
while True:
    envisionMain.update()
    event, values = window.read(timeout = 10)
    if event == 'foldload':
        set_selected_folder(values)

    if (event == 'parsefolder' and current_folder != None
                               and current_folder not in get_loaded_datasets()
                               and current_dataset != None):
        parse(current_folder)
    if event in setup_datasets(True):
        set_selected_dataset(event)
        switch_dataset(event)
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
window.close()

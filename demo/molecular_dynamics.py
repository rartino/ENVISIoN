#En primitiv fil för animaion av molekyldynamik.
#VASP_DIR behöver ändras och vissa visManager-funktioner behöver eventuellt läggas till

import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure" #ändra till rätt atom
HDF5_FILE = path_to_current_folder + "/../demo_molecular_dynamicts.hdf5"

#parse for molecular dynamics
envisionpy.hdf5parser.molecular_dynamics_parser(HDF5_FILE, VASP_DIR)

#clear any old network
inviwo.app.network.clear()

#Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("molecular dynamics")

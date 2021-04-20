import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/Cu_band_CUB"
#HDF5_FILE = path_to_current_folder + "/../demo_molecular_dynamics.hdf5"

#Temporär testning med färdig-genererad HDF5-fil
HDF5_FILE = path_to_current_folder + "/../md_test.hdf5"

#parse for molecular dynamics
#envisionpy.hdf5parser.mol_dynamic_parser(HDF5_FILE, VASP_DIR)

#clear any old network
inviwopy.app.network.clear()

#Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("molecular_dynamics")

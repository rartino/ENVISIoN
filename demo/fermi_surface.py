import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/FCC-Cu"
HDF5_FILE = path_to_current_folder + "/../demo_fermi.hdf5"

#envisionpy.hdf5parser.fermi_parser(HDF5_FILE, VASP_DIR)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("fermi")
visManager.subnetworks['fermi'].toggle_iso(True)
visManager.subnetworks['fermi'].clear_tf()

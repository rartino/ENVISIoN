import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

# Path to the vasp output directory you wish to visualise
VASP_DIR = path_to_current_folder + "/../unit_testing/resources/partial_charges"
HDF5_FILE = path_to_current_folder + "/../parchg.hdf5"

# Parse for charge density visualisation.
envisionpy.hdf5parser.parchg(HDF5_FILE, VASP_DIR)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("atom")
visManager.start("parchg", [1,2,3], ["total", "total", "total"])
visManager.subnetworks["parchg"].select_bands([1, 2], ["total", "total"])



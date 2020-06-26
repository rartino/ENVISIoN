import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

# Path to the vasp output directory you wish to visualise
VASP_DIR = path_to_current_folder + "/../unit_testing/resources/NaCl_charge_density"
HDF5_FILE = path_to_current_folder + "/../test3.hdf5"

# Parse for charge density visualisation.
envisionpy.hdf5parser.charge(HDF5_FILE, VASP_DIR)
envisionpy.hdf5parser.unitcell(HDF5_FILE, VASP_DIR)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("charge")
visManager.add_decoration("atom")
#visManager.add_decoration("charge")
#visManager.remove_decoration("atom")



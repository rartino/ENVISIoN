import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/TiPO4_DoS"
HDF5_FILE = path_to_current_folder + "/../dos_demo.hdf5"


envisionpy.hdf5parser.dos(HDF5_FILE, VASP_DIR)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("dos")
# visManager.main_visualisation.hide(False, True)


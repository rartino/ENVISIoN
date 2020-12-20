import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/Cu_band_CUB"
HDF5_FILE = path_to_current_folder + "/../demo_bandstruct2.hdf5"

# Parse for charge density visualisation.
envisionpy.hdf5parser.bandstructure(HDF5_FILE, VASP_DIR)
envisionpy.hdf5parser.fermi_energy(HDF5_FILE, VASP_DIR)


# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("band")
# visManager.main_visualisation.hide(False, True)


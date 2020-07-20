import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

# Path to the vasp output directory you wish to visualise
VASP_DIR = path_to_current_folder + "/../unit_testing/resources/NaCl_charge_density"
VASP_DIR2 = path_to_current_folder + "/../unit_testing/resources/TiPO4_ELF"
HDF5_FILE = path_to_current_folder + "/../unit_testing/resources/nacl18.hdf5"
HDF5_FILE2 = path_to_current_folder + "/../../HDF5-demo/charge_demo.hdf5"

# Parse for charge density visualisation.
envisionpy.hdf5parser.charge(HDF5_FILE, VASP_DIR)
#envisionpy.hdf5parser.elf(HDF5_FILE, VASP_DIR2)
#envisionpy.hdf5parser.unitcell(HDF5_FILE, VASP_DIR)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)

#visManager.start("elf")
visManager.start("charge")
#visManager.start("atom")
#visManager.stop("atom")
#visManager.start("atom")
#visManager.start("multi")



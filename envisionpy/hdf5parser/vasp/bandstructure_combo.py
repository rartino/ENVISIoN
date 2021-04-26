import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import h5py
from bandstructure import *
from fermiEnergy import *

def bandstructure_combo(HDF5_FILE, VASP_DIR):
    bandstructure(HDF5_FILE, VASP_DIR)
    fermi_energy(HDF5_FILE, VASP_DIR)

def bandstructure_combo3d(HDF5_FILE, VASP_DIR):
    bandstructure(HDF5_FILE, VASP_DIR)
    fermi_energy(HDF5_FILE, VASP_DIR)

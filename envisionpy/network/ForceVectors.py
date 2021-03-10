import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.LinePlotSubnetwork import LinePlotSubnetwork

class ForceVectors(LinePlotSubnetwork):
    '''
    Manages a subnetwork for electron localisation function (ELF) visualisation.
    Uses a default VolumeSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        LinePlotSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, False)

    @staticmethod
    def valid_hdf5(hdf5_file):
        return True

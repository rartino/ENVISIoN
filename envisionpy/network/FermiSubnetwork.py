import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.VolumeSubnetwork import VolumeSubnetwork

class FermiSubnetwork(VolumeSubnetwork):
    '''
    Manages a subnetwork for fermi surface/volume visualisation. 
    Uses a default VolumeSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        VolumeSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, False)

        # Set basis and volume path.
        with h5py.File(hdf5_path, "r") as h5:
            self.set_basis(np.array(h5["/reciprocal_basis/"], dtype='d'), 1)
        self.set_hdf5_subpath("/fermi_bands")
        
        # Set some default visualisation settings.
        # self.add_isovalue(0.5, [1, 1, 1, 1])
        self.set_iso_surface(0.5, [1, 1, 1, 1])
        self.add_tf_point(0.45, [0.1, 0.1, 0.8, 0.05])
        self.add_tf_point(0.5, [0.2, 0.8, 0.1, 0.1])
        self.add_tf_point(0.8, [0.9, 0.1, 0.1, 0.5])

    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("fermi_bands") != None

    def valid_decorations(self):
        return []


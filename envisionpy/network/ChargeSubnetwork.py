import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.VolumeSubnetwork import VolumeSubnetwork

class ChargeSubnetwork(VolumeSubnetwork):
    '''
    Manages a subnetwork for charge visualisation. 
    Uses a default VolumeSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        # Set up a generic volume rendering network.
        VolumeSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, False)
        
        # Set basis and volume path
        with h5py.File(hdf5_path, "r") as h5:
            self.set_basis(np.array(h5["/basis/"], dtype='d'), h5['/scaling_factor'][()])
        self.set_hdf5_subpath("/CHG")
        self.set_volume_selection('/final')
        self.set_volume_selection('/0')
        self.set_volume_selection('/final')

        # Set some default parameters for charge visualisation.
        self.add_tf_point(0.45, [0.1, 0.1, 0.8, 0.05])
        self.add_tf_point(0.5, [0.2, 0.8, 0.1, 0.1])
        self.add_tf_point(0.8, [0.9, 0.1, 0.1, 0.5])

    @staticmethod
    def valid_hdf5(hdf5_file):
        return (
            hdf5_file.get('CHG') != None and 
            len(hdf5_file.get('CHG').keys()) != 0 and
            hdf5_file.get('basis') != None and 
            hdf5_file.get('scaling_factor') != None)

    def valid_decorations(self):
        # Which decorations can be started while running this one.
        return ['atom']

    def disconnect_decoration(self, other, vis_type):
        if vis_type == 'atom':
            self.network.removeLink(self.camera_prop, other.camera_prop)
        self.disconnect_decorations_port(other.decoration_outport)

    def connect_decoration(self, other, vis_type):
        # Add a decoration by connecting data ports and linking properties.
        if vis_type not in self.valid_decorations():
            raise EnvisionError('Invalid decoration type ['+vis_type+'].')

        # Link needed properties between networks.
        if vis_type == 'atom':
            self.network.addLink(self.camera_prop, other.camera_prop)
        self.connect_decoration_ports(other.decoration_outport)


        # Connect ports.


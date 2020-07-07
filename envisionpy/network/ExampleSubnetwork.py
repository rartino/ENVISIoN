import inviwopy
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.Subnetwork import Subnetwork

class ExampleSubnetwork(Subnetwork):
    '''
    Example skeleton subnetwork for showing what functions should be included
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0):
        Subnetwork.__init__(self, inviwoApp)
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos)

        # Other initialization code here, default properties etc.

    @staticmethod
    def valid_hdf5(hdf5_file):
        # Test the hdf5 file and return if it is valid for this visualisation.
        return False

    def get_ui_data(self):
        # Return a list of data to show on the user interface.
        return []

    def valid_decorations(self):
        # Return a list of valid decorations.
        return []

    def connect_decoration(self, other, vis_type):
        # Connect properties and ports between visualisations.
        # Function only needed if there are valid decorations.
        if vis_type not in self.valid_decorations():
            raise EnvisionError('Invalid decoration type ['+vis_type+'].')

        self.connect_decoration_ports(other.decoration_outport)
    
    def disconnect_decoration(self, other, vis_type):
        # Disconnect properties and ports between visualisations.
        # Function only needed if there are valid decorations.

        self.disconnect_decorations_port(other.decoration_outport)

    def show(self):
        # Show this visualisation.
        pass

    def hide(self):
        # Hide this visualisation.
        pass

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        # Set up the processor network for this visualistion.

        # self.decoration_outport = 
        # self.decoration_inport = 
        pass

import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork

class Decoration(Subnetwork):
    '''
    Base decoration class
    '''
    def __init__(self, inviwoApp):
        Subnetwork.__init__(self, inviwoApp)
        self.other_subnetworks = {}
        #self.force_enabled = False

    def __del__(self):
        # Disconnect this from other networks.
        for vis_type, subnetwork in self.other_subnetworks.items():
            self.disconnect_decoration(subnetwork, vis_type)


    # Should be overloaded in inheritor class
    def valid_visualisations(self):
        return []

    # Should be overloaded in inheritor class
    def connect_decoration(self, other, vis_type):
        if vis_type not in self.valid_visualisations():
            raise EnvisionError('Invalid visualisation type ['+vis_type+'].')
        self.other_subnetworks[vis_type] = other

    # Should be overloaded in inheritor class
    def disconnect_decoration(self, other, vis_type):
        pass

    #Skissat från toggle_iso i VolumeSubnetwork.py rad 164
    # def toggle_force(self, enable)
    #     #Kolla om vi vill visa kraftvektorpilar
    #     self.force_enabled = enable
    #     #Kolla om nåt villkor (is_multichannel) är uppfyllt
    #     if self.is_multichannel:
    #         if enable:
    #             #Rita ut kraftvektorpilar
    #             set_force_vectors
    #         else:
    #             #Avaktivera utritning av kraftvektorpilar
    #             sätt inte ut kraftvektorpilar
    #     else:
    #         osäker på vad vi ska göra här
    #
    # def set_force_vectors(self, value, color=None):
    #     Skriv den här funktionen som ska rita ut alternativt
    #     ta bort kraftvektorpilar från visualiseringen

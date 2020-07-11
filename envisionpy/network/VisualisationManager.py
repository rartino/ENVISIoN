from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
import h5py
import numpy as np
from .AtomPositions import AtomPositions
from .PartialChargeDensity import PartialChargeDensity
from .ChargeDensity import ChargeDensity
from .ELFVolume import ELFVolume
from .FermiSurface import FermiSurface
from .Bandstructure import Bandstructure
from .DensityOfStates import DensityOfStates
from .MultiVolume import MultiVolume
from .baseNetworks.Decoration import Decoration

class VisualisationManager():
    '''
    Class for managing one visualisation instance from a single HDF5 file.
    '''
    def __init__(self, hdf5_path, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = {}
        self.decorations = {}

        self.main_vis_type = None
        self.available_visualisations = []

        self.hdf5_path = hdf5_path

        # Add hdf5 source processor
        self.hdf5Source = self.app.processorFactory.create('org.inviwo.hdf5.Source', glm.ivec2(0, 0))
        self.hdf5Source.filename.value = hdf5_path
        self.network.addProcessor(self.hdf5Source)
        self.hdf5Output = self.hdf5Source.getOutport('outport')

        # Check what visualisations are possible with this hdf5-file.
        with h5py.File(hdf5_path, 'r') as file:
            if ChargeDensity.valid_hdf5(file):
                self.available_visualisations.append("charge")
            if ELFVolume.valid_hdf5(file):
                self.available_visualisations.append("elf")
            if AtomPositions.valid_hdf5(file):
                self.available_visualisations.append("atom")
            if FermiSurface.valid_hdf5(file):
                self.available_visualisations.append("fermi")
            if PartialChargeDensity.valid_hdf5(file):
                self.available_visualisations.append("parchg")
            if Bandstructure.valid_hdf5(file):
                self.available_visualisations.append("band")
            if DensityOfStates.valid_hdf5(file):
                self.available_visualisations.append("dos")
            if len(set(['charge', 'elf', 'fermi', 'parchg']) & set(self.available_visualisations)) > 0:
                self.available_visualisations.append('multi')
                
    def start(self, vis_type, *args):
        # Start a new main visualisation.
        subnetwork = self.get_subnetwork(vis_type, *args)

        # Decoration visualisation.
        if issubclass(type(subnetwork), Decoration):
            self.decorations[vis_type] = subnetwork
            for other_type, other_network in self.subnetworks.items():
                if other_type in subnetwork.valid_visualisations():
                    subnetwork.connect_decoration(other_network, other_type)

        # Normal visualisation.
        else:
            # Try to connect running decorations to this one.
            for deco_network in self.decorations.values():
                if vis_type in deco_network.valid_visualisations():
                    deco_network.connect_decoration(subnetwork, vis_type)
            subnetwork.show()
            
        return subnetwork
        
    def stop(self, vis_type=None):
        if vis_type == None:
            # Stop all visualisations and clear networks.
            for subnetwork in self.subnetworks:
                subnetwork.clear_processors()
            self.network.removeProcessor(self.hdf5Source)
            return
        if vis_type not in self.subnetworks:
            raise EnvisionError('Tried to stop non running visualisation.')

        if vis_type in self.decorations:
            del self.decorations[vis_type]
        self.subnetworks[vis_type].clear_processors()
        del self.subnetworks[vis_type]

        

    # def start_decoration(self, target_vis, deco_type):
    #     # Add a visualisation as a decoration.
    #     if target_vis not in self.subnetworks:
    #         raise EnvisionError('Visualisation ['+target_vis+'] is not running. Start it before adding decoration.')
        
    #     subnetwork = self.get_subnetwork(deco_type)

    #     # self.subnetworks[target_vis].connect_decoration(subnetwork, deco_type)
    #     subnetwork.connect_decoration(self.subnetworks[target_vis], target_vis)

    #     # Try to add this decoration to running visualisations.
    #     return subnetwork
    
    def remove_decoration(self, vis_type, deco_type):
    # Remove decoration and clear that subnetwork.
        if vis_type not in self.subnetworks or deco_type not in self.subnetworks:
            raise EnvisionError('')
        self.subnetworks[vis_type].disconnect_decoration(self.subnetworks[deco_type], deco_type)

    def get_subnetwork(self, vis_type, *args):
        # Return the subnetwork for specified visualisation type.
        # If it does not exist, try to create it.

        if vis_type not in self.available_visualisations:
            raise EnvisionError('Cannot start visualisation ['+vis_type+'] with unsupported hdf5 file.')
        
        if vis_type in self.subnetworks:
            return self.subnetworks[vis_type]
        
        # Initialize a new subnetwork
        if vis_type == "charge":
            subnetwork = ChargeDensity(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "elf":
            subnetwork = ELFVolume(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "fermi":
            subnetwork = FermiSurface(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "parchg":
            subnetwork = PartialChargeDensity(self.app, self.hdf5_path, self.hdf5Output, 0, 3, *args)

        elif vis_type == "atom":
            subnetwork = AtomPositions(self.app, self.hdf5_path, self.hdf5Output, -20, 3)

        elif vis_type == "band":
            subnetwork = Bandstructure(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "dos":
            subnetwork = DensityOfStates(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "multi":
            subnetwork = MultiVolume(self.app, self.hdf5_path, self.hdf5Output, 30, 3)
            for t in ['charge', 'elf']:
                if t in self.subnetworks:
                    subnetwork.connect_volume(
                        self.subnetworks[t].volume_outport, 
                        self.subnetworks[t].transfer_function_prop, 
                        self.subnetworks[t].camera_prop)

        subnetwork.hide() # All new visualisations are hidden by default here.
        self.subnetworks[vis_type] = subnetwork
        return subnetwork

    def get_ui_data(self):
        data_packet = []
        data_packet.append(self.available_visualisations) # Available visualisations
        data_packet.append([]) # Active visualisations
        data_packet.append({}) # UI data for active visualisations.
        for vis_type, subnetwork in self.subnetworks.items():
            data_packet[1].append(vis_type)
            data_packet[2][vis_type] = subnetwork.get_ui_data()
        print(data_packet)
        return data_packet

    def call_subnetwork(self, vis_type, function_name, param_list):
        if function_name not in dir(self.get_subnetwork(vis_type)):
            raise EnvisionError("Invalid function call")
        return getattr(self.get_subnetwork(vis_type), function_name)(*param_list)
        
            
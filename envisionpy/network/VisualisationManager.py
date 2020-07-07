from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
import inviwopy.qt
import ivw.utils
import h5py
import numpy as np
from .AtomSubnetwork import AtomSubnetwork
from .ParchgSubnetwork import ParchgSubnetwork
from .ChargeSubnetwork import ChargeSubnetwork
from .ElfSubnetwork import ElfSubnetwork
from .FermiSubnetwork import FermiSubnetwork
from .BandSubnetwork import BandSubnetwork
from .DosSubnetwork import DosSubnetwork
from .MultiVolumeSubnetwork import MultiVolumeSubnetwork

class VisualisationManager():
    '''
    Class for managing one visualisation instance.
    '''
    def __init__(self, hdf5_path, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = {}

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
            if ChargeSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("charge")
            if ElfSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("elf")
            if AtomSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("atom")
            if FermiSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("fermi")
            if ParchgSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("parchg")
            if BandSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("band")
            if DosSubnetwork.valid_hdf5(file):
                self.available_visualisations.append("dos")
            if len(set(['charge', 'elf', 'fermi', 'parchg']) & set(self.available_visualisations)) > 0:
                self.available_visualisations.append('multi')
        print("Available vis types: ", self.available_visualisations)

    def start(self, vis_type, *args):
        # Start a new main visualisation.
        subnetwork = self.get_subnetwork(vis_type, *args)
        subnetwork.show()
        return subnetwork
        
    def stop(self, vis_type=None):
        if vis_type == None:
            # Stop all visualisations and clear networks.
            for subnetwork in self.subnetworks:
                subnetwork.clear_processors()
            self.network.removeProcessor(self.hdf5Source)
        else:
            self.subnetworks[vis_type].clear_processors()
            del self.subnetworks[vis_type]

    def add_decoration(self, target_vis, deco_type):
        # Add a visualisation as a decoration.
        if target_vis not in self.subnetworks:
            raise EnvisionError('Visualisation ['+target_vis+'] is not running. Start it before adding decoration.')
        
        subnetwork = self.get_subnetwork(deco_type)

        self.subnetworks[target_vis].connect_decoration(subnetwork, deco_type)
        return subnetwork
    
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
            subnetwork = ChargeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            self.get_subnetwork('multi').connect_volume(
                subnetwork.volume_outport, 
                subnetwork.transfer_function_prop, 
                subnetwork.camera_prop)

        elif vis_type == "elf":
            subnetwork = ElfSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            self.get_subnetwork('multi').connect_volume(
                subnetwork.volume_outport, 
                subnetwork.transfer_function_prop, 
                subnetwork.camera_prop)

        elif vis_type == "fermi":
            subnetwork = FermiSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            self.get_subnetwork('multi').connect_volume(
                subnetwork.volume_outport, 
                subnetwork.transfer_function_prop, 
                subnetwork.camera_prop)

        elif vis_type == "parchg":
            subnetwork = ParchgSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3, *args)

        elif vis_type == "atom":
            subnetwork = AtomSubnetwork(self.app, self.hdf5_path, self.hdf5Output, -20, 3)

        elif vis_type == "band":
            subnetwork = BandSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "dos":
            subnetwork = DosSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "multi":
            subnetwork = MultiVolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 30, 3)

        subnetwork.hide() # All new visualisations are hidden by default here.
        self.subnetworks[vis_type] = subnetwork
        return subnetwork
        
            
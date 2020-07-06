from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
import h5py
import numpy as np
from .AtomSubnetwork import AtomSubnetwork
from .ParchgSubnetwork import ParchgSubnetwork
from .ChargeSubnetwork import ChargeSubnetwork
from .ElfSubnetwork import ElfSubnetwork
from .FermiSubnetwork import FermiSubnetwork
from .BandSubnetwork import BandSubnetwork
from .DosSubnetwork import DosSubnetwork

class VisualisationManager():
    '''
    Class for managing one visualisation instance.
    '''
    def __init__(self, hdf5_path, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = {}
        self.active_visualisations = []

        self.main_visualisation = None
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

        print("Available vis types: ", self.available_visualisations)

    def start(self, vis_type, *args):
        subnetwork = self.create_subnetwork(vis_type, *args)
        subnetwork.show()
        
    def stop(self):
        for subnetwork in self.subnetworks:
            subnetwork.clear_processors()
        self.network.removeProcessor(self.hdf5Source)

    def add_decoration(self, target_vis, deco_type):
        if target_vis not in self.subnetworks:
            raise EnvisionError('Visualisation ['+target_vis+'] is not running. Start it before adding decoration.')

        if deco_type in self.subnetworks:
            subnetwork = self.subnetworks[deco_type]
        else:
            subnetwork = self.create_subnetwork(deco_type)
        self.subnetworks[target_vis].connect_decoration(subnetwork, deco_type)
    
    def remove_decoration(self, vis_type, deco_type):
    # Remove decoration and clear that subnetwork.
        if vis_type not in self.subnetworks or deco_type not in self.subnetworks:
            raise EnvisionError('')
        self.subnetworks[vis_type].disconnect_decoration(self.subnetworks[deco_type], deco_type)

    def create_subnetwork(self, vis_type, *args):
        # Add add a subnetwork for a specific visualisation type.
        # Max one network per visualisation type is created.

        if vis_type not in self.available_visualisations:
            raise EnvisionError('Cannot start visualisation ['+vis_type+'] with unsupported hdf5 file.')
        
        # if vis_type in self.subnetworks:
        #     return self.subnetworks[vis_type]
        
        # Initialize a new subnetwork
        if vis_type == "charge":
            self.supported_decorations = ["elf", "atom"]
            subnetwork = ChargeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "elf":
            subnetwork = ElfSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "fermi":
            subnetwork = FermiSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "atom":
            subnetwork = AtomSubnetwork(self.app, self.hdf5_path, self.hdf5Output, -20, 3)

        elif vis_type == "parchg":
            subnetwork = ParchgSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3, *args)
            with h5py.File(self.hdf5_path, "r") as h5:
                subnetwork.set_basis(np.array(h5["/basis/"], dtype='d'), h5['/scaling_factor'][()])

        elif vis_type == "band":
            subnetwork = BandSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "dos":
            subnetwork = DosSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        subnetwork.hide() # All new visualisations are hidden by default here.
        self.subnetworks[vis_type] = subnetwork
        return subnetwork
        

            
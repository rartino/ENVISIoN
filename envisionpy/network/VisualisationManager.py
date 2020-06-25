from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
from .VolumeSubnetwork import VolumeSubnetwork
from .AtomSubnetwork import AtomSubnetwork

class VisualisationManager():
    def __init__(self, hdf5_path, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = []
        self.hdf5_path = hdf5_path

        # Add hdf5 source processor
        self.hdf5Source = self.app.processorFactory.create('org.inviwo.hdf5.Source', glm.ivec2(0, 0))
        self.hdf5Source.filename.value = hdf5_path
        self.network.addProcessor(self.hdf5Source)
        self.hdf5Output = self.hdf5Source.getOutport('outport')

    def stop(self):
        for subnetwork in self.subnetworks:
            subnetwork.clear_processors()
        self.network.removeProcessor(self.hdf5Source)

    def add_subnetwork(self, network_type):
        if network_type == "charge":
            subnetwork = VolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            subnetwork.set_hdf5_subpath("/CHG")
            subnetwork.set_volume_selection('/final')
        elif network_type == "elf":
            subnetwork = VolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 15)
            subnetwork.set_hdf5_subpath("/ELF")
            subnetwork.set_volume_selection('/final')
        elif network_type == "atom":
            subnetwork = AtomSubnetwork(self.app, self.hdf5_path, self.hdf5Output, -15, 3)
        self.subnetworks.append(subnetwork)

            
        

    

    
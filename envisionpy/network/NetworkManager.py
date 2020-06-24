from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
from .VolumeSubnetwork import VolumeSubnetwork
from .AtomSubnetwork import AtomSubnetwork

class NetworkManager():
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


        # # Add background
        # self.background = self.app.processorFactory.create('org.inviwo.Background', glm.ivec2(0, 25*18))
        # self.network.addProcessor(self.background)
        # self.canvas_inport = self.background.getInport('inport')

        # # Add canvas
        # self.canvas = self.app.processorFactory.create('org.inviwo.CanvasGL', glm.ivec2(0, 25*21))
        # self.network.addProcessor(self.canvas)
        # self.network.addConnection(self.background.getOutport('outport'), self.canvas.getInport('inport'))

    def stop(self):
        # Clear subnetworks and self
        pass

    def add_subnetwork(self, network_type):
        if network_type == "charge":
            print("HDF5 STATUS: ", VolumeSubnetwork.check_hdf5(self.hdf5_path, "/CHG"))
            subnetwork = VolumeSubnetwork(self.app, 0, 3)
            subnetwork.connect_hdf5(self.hdf5Output)
            subnetwork.set_hdf5_subpath("/CHG")
            self.subnetworks.append(subnetwork)
            print(subnetwork.image_outport)
            # subnetwork.connect_image(self.canvas_inport)

        if network_type == "atom":
            subnetwork = AtomSubnetwork(self.app, self.hdf5_path, self.hdf5Output, -15, 3)
            self.subnetworks.append(subnetwork)

            
        

    

    
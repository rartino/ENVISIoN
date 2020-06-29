from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
import h5py
import numpy as np
from .VolumeSubnetwork import VolumeSubnetwork
from .AtomSubnetwork import AtomSubnetwork

class VisualisationManager():
    def __init__(self, hdf5_path, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = {}

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
            if file.get("CHG") != None and len(file.get("CHG").keys()) != 0:
                self.available_visualisations.append("charge")
            if file.get("ELF") != None and len(file.get("ELF").keys()) != 0:
                self.available_visualisations.append("elf")
            if file.get("UnitCell") != None:
                self.available_visualisations.append("atom")
            if file.get("fermi_bands") != None:
                self.available_visualisations.append("fermi")

        print("Available vis types: ", self.available_visualisations)

    def start(self, vis_type):
    # Start a main visualisation
        if self.main_visualisation != None:
            raise ProcessorNetworkError('Main visualisation already started.')
        self.main_visualisation = self.add_subnetwork(vis_type)
        self.main_vis_type = vis_type
        self.main_visualisation.show()

    def stop(self):
        for subnetwork in self.subnetworks:
            subnetwork.clear_processors()
        self.network.removeProcessor(self.hdf5Source)

    def add_decoration(self, vis_type):
    # Add decoration to main visualisation.
        # TODO: check if decoration type is compatible with main visualisation.
        print("Connecting decoration ", vis_type)
        subnetwork = self.add_subnetwork(vis_type)
        self.main_visualisation.connect_3d_decoration(subnetwork.decoration_outport, subnetwork.camera_prop)
    
    def remove_decoration(self, vis_type):
    # Remove decoration and clear that subnetwork.
        if not vis_type in self.subnetworks:
            return
        
        self.main_visualisation.disconnect_3d_decoration(self.subnetworks[vis_type].decoration_outport)

        if vis_type != self.main_vis_type:
            self.subnetworks[vis_type].clear_processors()
            del self.subnetworks[vis_type]

    def add_subnetwork(self, vis_type):
    # Add add a subnetwork for a specific visualisation type.
    # Max one network per visualisation type is created.
        if not vis_type in self.available_visualisations:
            raise BadHDF5Error('Tried to start visualisation with unsupported hdf5 file.')
        if vis_type in self.subnetworks:
            return self.subnetworks[vis_type]
        
        # Initialize a new subnetwork
        if vis_type == "charge":
            self.supported_decorations = ["elf", "atom"]
            subnetwork = VolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            with h5py.File(self.hdf5_path, "r") as h5:
                basis_3x3 = np.array(h5["/basis/"], dtype='d')
                scale = h5['/scaling_factor'][()]
                subnetwork.set_basis(basis_3x3, scale)
            subnetwork.set_hdf5_subpath("/CHG")
            subnetwork.set_volume_selection('/final')
        elif vis_type == "elf":
            subnetwork = VolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            with h5py.File(self.hdf5_path, "r") as h5:
                basis_3x3 = np.array(h5["/basis/"], dtype='d')
                scale = h5['/scaling_factor'][()]
                subnetwork.set_basis(basis_3x3, scale)
            subnetwork.set_hdf5_subpath("/ELF")
            subnetwork.set_volume_selection('/final')
        elif vis_type == "fermi":
            subnetwork = VolumeSubnetwork(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            with h5py.File(self.hdf5_path, "r") as h5:
                basis_3x3 = np.array(h5["/reciprocal_basis/"], dtype='d')
                subnetwork.set_basis(basis_3x3, 1)
            subnetwork.set_hdf5_subpath("/fermi_bands")
        elif vis_type == "atom":
            subnetwork = AtomSubnetwork(self.app, self.hdf5_path, self.hdf5Output, -20, 3)
        subnetwork.hide() # All new visualisations are hidden by default, show elsewhere.
        self.subnetworks[vis_type] = subnetwork
        return subnetwork
        

            
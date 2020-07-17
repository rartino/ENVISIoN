import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.VolumeSubnetwork import VolumeSubnetwork

# TODO: Link the tf properties instead and copying will be done automatically.
#       Inviwo bug is preventing this as of writing.

# TODO: Closing one of the connected volume visualisations while this one is running
#       Will result in unsupported behaviour. Either block those from closing before
#       this, notify this about them closing, or restart this when volume is closed.

class MultiVolume(VolumeSubnetwork):
    '''
    Manages a subnetwork for rendering of multiple volumes from other visualisations. 
    Takes multiple volumes and transfer functions and renders them in a single image.
    Used to for example render both Electron Density and ELF in the same canvas. 

    Based on a modified VolumeSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        # Set up a generic volume rendering network.
        VolumeSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, True)
        self.modify_network(xpos, ypos)

        self.used_inports = [False] * 4
        self.other_transferfunctions = [None] * 4
        
    @staticmethod
    def valid_hdf5(hdf5_file):
        return (
            hdf5_file.get('CHG') != None and 
            len(hdf5_file.get('CHG').keys()) != 0 and
            hdf5_file.get('basis') != None and 
            hdf5_file.get('scaling_factor') != None)

    def get_ui_data(self):
        return []

    def copy_transferfunctions(self):
        # Copy all the transferfunctions from connected visualisations.
        # TODO: Link the properties instead and this will be done automatically.
        #       Inviwo bug is preventing this as of writing.
        for i, connected in enumerate(self.used_inports):
            if not connected: continue
            tf_points = self.other_transferfunctions[i].getValues()
            self.transfer_functions[i].clear()
            for p in tf_points:
                self.transfer_functions[i].add(p)

            if tf_points[0].pos != 0:
                self.transfer_functions[i].add(
                    tf_points[0].pos * 0.99,
                    inviwopy.glm.vec4(1.0, 1.0, 1.0, 0.0))



    def connect_volume(self, volume_outport, transfer_func_prop, camera_prop):
        if all(self.used_inports):
            raise EnvisionError('No more than 4 volumes may be connected.')

        
        self.network.addLink(self.camera_prop, camera_prop)
        self.network.addLink(camera_prop, self.camera_prop)

        idx = self.used_inports.index(False)
        self.used_inports[idx] = True
        self.other_transferfunctions[idx] = transfer_func_prop
        self.network.addConnection(volume_outport, self.volume_inports[idx])

        # Inviwo bug preventing linking of TransferFunctionProperty.
        # self.network.addLink(transfer_func_prop.tf, self.transfer_functions[idx])
        # self.network.addLink(self.transfer_functions[idx], transfer_func_prop.tf)
        self.copy_transferfunctions() # Remove when bug is fixed.

    def modify_network(self, xpos, ypos):
        self.remove_processor('HDF5 path')
        self.remove_processor('Hdf5Selection')
        merger = self.add_processor('org.inviwo.VolumeMerger', 'VolumeMerger', xpos, ypos + 3)

        boundingBox = self.get_processor('Volume Bounding Box')
        cubeProxy = self.get_processor('Cube Proxy Geometry')
        raycaster = self.get_processor('Raycaster')
        volumeSlice = self.get_processor('VolumeSlice')
        isoRaycaster = self.get_processor('IsoRaycaster')
        self.network.addConnection(merger.getOutport('outputVolume'), boundingBox.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), cubeProxy.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), raycaster.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), isoRaycaster.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), volumeSlice.getInport('volume'))

        self.volume_inports = [
            merger.getInport('inputVolume'),
            merger.getInport('volume2'),
            merger.getInport('volume3'),
            merger.getInport('volume4')
        ]
        self.transfer_functions = [
            getattr(raycaster, 'transfer-functions').transferFunction1,
            getattr(raycaster, 'transfer-functions').transferFunction2,
            getattr(raycaster, 'transfer-functions').transferFunction3,
            getattr(raycaster, 'transfer-functions').transferFunction4
        ]
        pass




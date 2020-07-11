import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.VolumeSubnetwork import VolumeSubnetwork


# TODO: add self.volume_outport with a merged version of all the 
#       volumes. Use a VolumeCombiner processor and input all volumes
#       add data divide by number of volumes. Output of this is volume_outport
#       This will allow the visualisation to be used with the multi volume vis.

class PartialChargeDensity(VolumeSubnetwork):
    '''
    Manages a subnetwork for partial charge density visualisation. 
    Makes use of a modified VolumeSubnetwork. Has a different volume selection than 
    the default VolumeSubnetwork implementation to allow selection of different bands
    and modes.

    Based on VolumeSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0, band_list=[], mode_list=[]):
        # Initialize a volume subnetwork with multichannel raycaster
        VolumeSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos+6, True)
        self.set_hdf5_subpath('PARCHG/Bands')
        
        # Available bands and modes in hdf5 file.
        self.available_bands = []
        self.available_modes = []
        with h5py.File(hdf5_path, 'r') as file:
            for key in file.get("PARCHG/Bands").keys():
                self.available_bands.append(key)
            for key in file.get("PARCHG/Bands")[self.available_bands[0]].keys():
                self.available_modes.append(key)
            if ("magnetic" in self.available_modes) and ("total" in self.available_modes):
                self.available_modes += ["up", "down"]

            # self.set_basis(np.array(h5["/basis/"], dtype='d'), h5['/scaling_factor'][()])

        self.current_bands = []
        self.current_modes = []

        self.volume_processors = []
        self.basis_props = []
        self.basis_3x3 = [[1,0,0],[0,1,0],[0,0,1]]
        self.basis_scale = 1
        
        # Modify network for parchg visualisation.
        self.modify_network(hdf5_path, hdf5_outport, xpos, ypos)
        self.select_bands(band_list, mode_list, xpos+1, ypos)

        with h5py.File(hdf5_path, "r") as h5:
            self.set_basis(np.array(h5["/basis/"], dtype='d'), h5['/scaling_factor'][()])

        # Set some default parameters for charge visualisation.
        self.add_tf_point(0.45, [0.1, 0.1, 0.8, 0.05])
        self.add_tf_point(0.5, [0.2, 0.8, 0.1, 0.1])
        self.add_tf_point(0.8, [0.9, 0.1, 0.1, 0.5])

    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("PARCHG") != None

    def valid_decorations(self):
        return ['atom']

    def connect_decoration(self, other, vis_type):
        if vis_type not in self.valid_decorations():
            raise EnvisionError('Invalid decoration type ['+vis_type+'].')
        # Link needed properties between networks.
        if vis_type == 'atom':
            self.network.addLink(self.camera_prop, other.camera_prop)
        self.connect_decoration_ports(other.decoration_outport)

    def disconnect_decoration(self, other, vis_type):
        if vis_type == 'atom':
            self.network.removeLink(self.camera_prop, other.camera_prop)
        self.disconnect_decorations_port(other.decoration_outport)


    def get_available_modes(self):
        return self.available_modes

    def get_available_bands(self):
        return self.available_bands

    def get_partial_selections(self):
        return [self.current_bands, self.current_modes]

# ------------------------------------------
# ------- Property control functions -------

    def set_basis(self, basis_3x3, scale=1):
        self.basis_3x3 = basis_3x3
        basis_4x4 = np.identity(4)
        basis_4x4[:3,:3] = basis_3x3
        basis_4x4 = np.multiply(scale, basis_4x4)
        minValue = inviwopy.glm.mat4(
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000)
        maxValue = inviwopy.glm.mat4(
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000)
        value = inviwopy.glm.mat4(*basis_4x4.flatten())
        for basis_prop in self.basis_props:
            basis_prop.minValue = minValue
            basis_prop.maxValue = maxValue
            basis_prop.value = value

        meshCreator = self.get_processor('MeshCreator')
        meshCreator.scale.value = scale

# ------------------------------------------
# ------- Network building functions -------


    def select_bands(self, band_list, mode_list, xpos=1, ypos=0):
        # Connect and merge up to 4 different volumes with the different modes.

        # Validate input.
        if len(band_list) != len(mode_list):
            raise EnvisionError('Mode list must be same length as band list for partial charge visualisation.')
        if len(band_list) > 4:
            raise EnvisionError('A maximum of 4 volumes can be used at one time for partial charge visualisation.')
        for mode in mode_list:
            if mode not in self.available_modes:
                raise EnvisionError('Unavailable mode. Data for [' + str(mode) + '] mode not in hdf5 file.')
        for band in band_list:
            if str(band) not in self.available_bands:
                raise EnvisionError('Unavailable band. Data for band [' + str(band) + '] not in hdf5 file.')

        self.current_bands = band_list
        self.current_modes = mode_list

        # Clear any old volume selection
        for processor in self.volume_processors:
            self.remove_processor_by_ref(processor)
        self.basis_props.clear()
        self.volume_processors.clear()

        # Set up new volume selections according to band and mode selections.
        hdf5_inports = []
        volume_outports = []
        for i in range(len(band_list)):
            if mode_list[i] == 'total' or mode_list[i] == 'magnetic':
                volumeTotal = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' ' + mode_list[i], xpos+7*(i+1), ypos+3)
                self.basis_props.append(volumeTotal.basisGroup.basis)
                self.volume_processors.append(volumeTotal)
                hdf5_inports.append(volumeTotal.getInport('inport'))
                volume_outports.append(volumeTotal.getOutport('outport'))
            else:
                volumeInPlus = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' total', xpos+7*(i+1), ypos+3)
                volumeInMinus = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' magnetic', xpos-1+7*(i+1) , ypos+6)
                volumeCombine = self.add_processor('org.inviwo.VolumeCombiner', 'Band ' + str(band_list[i]) + ' ' + mode_list[i], xpos+7*(i+1), ypos+9)

                self.network.addConnection(volumeInPlus.getOutport('outport'), volumeCombine.getInport('inport'))
                self.network.addConnection(volumeInMinus.getOutport('outport'), volumeCombine.getInport('inport'))

                if mode_list[i] == 'up':
                    volumeCombine.eqn.value = '0.5*(v1+v2)'
                if mode_list[i] == 'down':
                    volumeCombine.eqn.value = '0.5*(v1-v2)'

                self.basis_props.append(volumeInPlus.basisGroup.basis)
                self.basis_props.append(volumeInMinus.basisGroup.basis)
                hdf5_inports.append(volumeInPlus.getInport('inport'))
                hdf5_inports.append(volumeInMinus.getInport('inport'))
                volume_outports.append(volumeCombine.getOutport('outport'))
                self.volume_processors += [volumeInPlus, volumeInMinus, volumeCombine]

        self.set_basis(self.basis_3x3, self.basis_scale)

        # Connect the hdf5 inports and volume outports.
        hdf5Path = self.get_processor('HDF5 path')
        merger = self.get_processor('VolumeMerger')
        volume_inports = [
            merger.getInport('inputVolume'), merger.getInport('volume2'), 
            merger.getInport('volume3'), merger.getInport('volume4')]
        for inport in hdf5_inports:
            self.network.addConnection(hdf5Path.getOutport('outport'), inport)
        for i in range(len(volume_outports)):
            self.network.addConnection(volume_outports[i], volume_inports[i])

    def modify_network(self, hdf5_path, hdf5_output, xpos, ypos):
        # Change the volume selection compared to the default volume network.
        
        # Remove hdf5ToVolume processor.
        self.remove_processor('Hdf5Selection')

        # Create and connect volume merger.
        merger = self.add_processor('org.inviwo.VolumeMerger', 'VolumeMerger', xpos, ypos + 9)
        
        isoRaycaster = self.get_processor('IsoRaycaster')
        boundingBox = self.get_processor('Volume Bounding Box')
        cubeProxy = self.get_processor('Cube Proxy Geometry')
        raycaster = self.get_processor('Raycaster')
        volumeSlice = self.get_processor('VolumeSlice')

        self.network.addConnection(merger.getOutport('outputVolume'), boundingBox.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), cubeProxy.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), raycaster.getInport('volume'))
        self.network.addConnection(merger.getOutport('outputVolume'), volumeSlice.getInport('volume'))
        if self.is_multichannel:
            isoRaycaster = self.get_processor('IsoRaycaster')
            self.network.addConnection(merger.getOutport('outputVolume'), isoRaycaster.getInport('volume'))
        


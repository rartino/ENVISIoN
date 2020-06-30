import inviwopy
import ivw.utils
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .VolumeSubnetwork import VolumeSubnetwork


class ParchgSubnetwork(VolumeSubnetwork):
    '''
    Manages a subnetwork for multichannel volume rendering. 
    Used for the partial charge density visualisation.

    Makes use of a modified VolumeSubnetwork. Modifies volume selection and 
    raycaster is replaced by a multichannel raycaster.

    Overloads some raycaster related functions to work with the multichannel raycaster.    
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

        self.volume_processors = []
        
        # Modify network for parchg visualisation.
        self.modify_network(hdf5_path, hdf5_outport, xpos, ypos)
        self.select_bands([1], ['total'])
        # self.select_bands([4, 3, 2, 1], ['up', 'down', 'up', 'down'])

    def get_available_modes(self):
        return self.available_modes

    def get_available_bands(self):
        return self.available_bands
# ------------------------------------------
# ------- Property control functions -------
    def set_basis(self, basis_3x3, scale=1):
        basis_4x4 = np.identity(4)
        basis_4x4[:3,:3] = basis_3x3
        basis_4x4 = np.multiply(scale, basis_4x4)
        hdf5Volume = self.get_processor('Hdf5Selection')
        hdf5Volume.basisGroup.basis.minValue = inviwopy.glm.mat4(
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000)
        hdf5Volume.basisGroup.basis.maxValue = inviwopy.glm.mat4(
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000)
        hdf5Volume.basisGroup.basis.value = inviwopy.glm.mat4(*basis_4x4.flatten())
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

        # Clear any old volume selection
        for processor in self.volume_processors:
            print(processor)
            self.remove_processor_by_ref(processor)
        self.volume_processors.clear()

        # Set up new volume selections according to band and mode selections.
        hdf5_inports = []
        volume_outports = []
        for i in range(len(band_list)):
            if mode_list[i] == 'total' or mode_list[i] == 'magnetic':
                volumeTotal = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' ' + mode_list[i], xpos+7*(i+1), ypos+3)
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

                hdf5_inports.append(volumeInPlus.getInport('inport'))
                hdf5_inports.append(volumeInMinus.getInport('inport'))
                volume_outports.append(volumeCombine.getOutport('outport'))
                self.volume_processors += [volumeInPlus, volumeInMinus, volumeCombine]

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
        


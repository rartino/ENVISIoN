#
#  ENVISIoN
#
#  Copyright (c) 2018 Jesper Ericsson
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################
#
#  Alterations to this file by Jesper Ericsson
#  and Andreas Kempe
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import os,sys
import inspect
import inviwopy
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))
import numpy as np
import h5py
import math

from .VolumeNetworkHandler import VolumeNetworkHandler
from .UnitcellNetworkHandler import UnitcellNetworkHandler

# TODO: Files parsed for parchg does not seem to work. Inviwo seems to not recognize the datasets as valid volumes.
#       May have something to do with the different size of the volume data in hdf5 file. 
#       Parchg is 24x24x24 while charge, which works, is 48x48x48.
#       Analyze and compare files with "HDFView" tool to see diferences between datasets.

# TODO: merger_list in setup_band_processors function looks a bit funky to me.
#       How the nestled for loops build the list is not great, some recursion instead?
#       Current setup will probably not handle if more than 16 bands are used at the same time
#       Low prio fix as that is a lot of bands and you dont often need that many i think. 

# TODO: Add UnitcellNetworkHandler as parent. Check ChargeNetworkHandler too see how.

# TODO: Add more property controls? Probably no more needed? 

# TODO: Add some way to get available bands.

class ParchgNetworkHandler(VolumeNetworkHandler, UnitcellNetworkHandler):
    """ Class for setting up and handling the inviwo network for partial charge visualization
    """
    def __init__(self, hdf5_path, inviwoApp, band_list=[], mode_list=[]):
        """ Initializes the partial charge network 
        Parameters:
        hdf5_path : str
            Path to HDF5 file
        band_list : list of int
            List containing the band numbers for the bands to be visualised 
        mode_list : list of int
            Specifies how to visualize a specific band. In the order you enumerated your bands in band_list, choose mode where
            0 for 'total'
            1 for 'magnetic'
            2 for 'up'
            3 for 'down'
            Example: If band_list is [31, 212] and mode_list is [1,3], band 31 will be visualized as 'magnetic' and 212 as 'down'
        """
        self.processors = {}
        self.hdf5_path = hdf5_path
        VolumeNetworkHandler.__init__(self, inviwoApp)

        # Unitcell is not critical to visualization, if it fails, continnue anyway
        self.unitcellAvailable = True
        try: 
            UnitcellNetworkHandler.__init__(self, hdf5_path, inviwoApp)
        except AssertionError as error:
            print(error)
            self.unitcellAvailable = False

        # Check if  hdf5-file is valid
        with h5py.File(hdf5_path, 'r') as file:
            if file.get("PARCHG/Bands") == None:
                raise AssertionError("No valid partial charge data in that file")
        if len(self.get_available_bands()[0]) == 0:
            raise AssertionError("No valid partial charge data in that file")

        self.setup_parchg_network(hdf5_path)
        self.setup_band_processors(band_list, mode_list)

        self.hdf5_path = hdf5_path
        self.HDFvolume_processors = []
        self.merger_processors = []
        self.current_bands = band_list
        self.current_modes = mode_list

        # Setup default unitcell settings
        if self.unitcellAvailable:
            self.toggle_full_mesh(False)
            self.toggle_unitcell_canvas(False)

    def select_bands(self, band_list, mode_list):
    # Re-selects bands. Clears old bands and adds the new ones.
        self.clear_band_processors()
        self.setup_band_processors(band_list, mode_list)
        self.current_bands = band_list
        self.current_modes = mode_list

    def get_available_bands(self):
    # Return the keys to the available parchg bands in hdf5-file
        with h5py.File(self.hdf5_path, 'r') as file:
            band_keys = []
            for key in file.get("PARCHG/Bands").keys():
                band_keys.append(key)
            return band_keys

    def get_available_modes(self):
    # Return a list of available modes for hdf5 file
        bands = self.get_available_bands()
        with h5py.File(self.hdf5_path, 'r') as file:
            modes = []
            for key in file.get("PARCHG/Bands")[bands[0]].keys():
                modes.append(key)
        if "magnetic" in modes:
            modes += ["up", "down"]
        return modes

# ------------------------------------------
# ------- Network building functions -------

    def clear_band_processors(self):
    # Removes all the band selection and merging processors

        for i in self.merger_processors:
            if type(i) is list:
                for j in i:
                    self.remove_processor_by_ref(j)
            else:
                self.remove_processor_by_ref(i)
        for i in self.HDFvolume_processors:
            if type(i) is list:
                for j in i:
                    self.remove_processor_by_ref(j)
            else:
                self.remove_processor_by_ref(i)

        self.merger_processors = []
        self.HDFvolume_processors = []
        self.current_bands = []
        self.current_modes = []

    def merger_calc(self, l, previous_level):
        """ Calculates the number of volume merger processors needed per level recursively
        Parameters:
        l : list of int
        Partial list in the recursive algorithm. Is initially empty.
        level : int
        How many processors exist on the level above the current. Is intially the number of
        HDFToVolume processors.

        Returns
        ------
        list

        """
        if previous_level != 1:
            level = math.ceil(previous_level/4)
            l.append(level)
            l = self.merger_calc(l,level)
        return l

    

    def setup_parchg_network(self, hdf5_path):
        self.HDFsource = self.add_h5source(hdf5_path, -100, 0)
        # self.HDFsource.filename.value = hdf5_path

        # Connect unitcell and volume visualisation.
        volumeBoxRenderer = self.get_processor('Mesh Renderer')
        unitcellRenderer = self.get_processor('Unit Cell Renderer')
        if volumeBoxRenderer and unitcellRenderer:
            self.network.addConnection(unitcellRenderer.getOutport('image'), volumeBoxRenderer.getInport('imageInport'))
            self.network.addLink(unitcellRenderer.getPropertyByIdentifier('camera'), volumeBoxRenderer.getPropertyByIdentifier('camera'))
            self.network.addLink(volumeBoxRenderer.getPropertyByIdentifier('camera'), unitcellRenderer.getPropertyByIdentifier('camera'))

    def setup_band_processors(self, band_list, mode_list):
        """ Sets up the processors to handle the different band selections and modes, along with merging the resulting volumes.
            Is called in build_network function when initializing class
            Can be called after building network to change selection without rebuilding whole network
        Parameters:
        band_list : list of int
            List containing the band numbers for the bands to be visualised.
        mode_list : list of int
            List that specifies what mode the individual bands should be visualized in.
        """
        
        xpos = 200-8*25
        ypos = -400+6*25

        
        n_bands = len(band_list)
        if n_bands == 0:
            print("No bands selected")
            return
        if len(band_list) != len(mode_list):
            raise Exception("Unequal bands and modes. Each band must have one corresponding mode.")
        
        level_list = []
        level_list = self.merger_calc(level_list, n_bands)
        HDFvolume_list = []
        merger_list = []

        # Add the different HDF5 to volume processors for each band
        mode_dict = ['total','magnetic','up','down']
        for i in range(0, n_bands):
            if mode_list[i] == 0 or mode_list[i] == 1:
                volumeTotal = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' ' + mode_dict[mode_list[i]], xpos + 180*i, ypos+225)
                HDFvolume_list.append(volumeTotal)
            else:
                volumeInPlus = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' total', xpos + 180*i, ypos+75)
                volumeInMinus = self.add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(band_list[i]) + ' magnetic', xpos + 180*i+25, ypos+150)
                volumeCombine = self.add_processor('org.inviwo.VolumeCombiner', 'Band ' + str(band_list[i]) + ' ' + mode_dict[mode_list[i]], xpos + 180*i, ypos+225)

                if mode_list[i] == 2:
                    volumeCombine.eqn.value = '0.5*(v1+v2)'
                if mode_list[i] == 3:
                    volumeCombine.eqn.value = '0.5*(v1-v2)'
                
                HDFvolume_list.append([volumeInPlus, volumeInMinus, volumeCombine])

        for i in range(0, len(level_list)):
            submerger_list = []
            for j in range(0, level_list[i]):
                submerger_list.append(self.add_processor('org.inviwo.VolumeMerger', 'Level ' + str(i+1) + '  unit ' + str(j+1), xpos + 180*j, ypos + 300 + 75*i))
            merger_list.append(submerger_list)
        
        # Save the processors to class variables for later access
        self.HDFvolume_processors = HDFvolume_list
        self.merger_processors = merger_list

        # Connections from the source and the HDF5ToVolume blocks
        # Also add volume mergers
        for i in range(0, n_bands):
            if mode_list[i] == 0 or mode_list[i] == 1:
                self.network.addConnection(self.HDFsource.getOutport('outport'), HDFvolume_list[i].getInport('inport'))
                if merger_list:
                    if ((i+1) % 4) == 1:
                        self.network.addConnection(HDFvolume_list[i].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('inputVolume'))
                    else:
                        self.network.addConnection(HDFvolume_list[i].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('volume'+str((i%4)+1)))
                
            else:
                self.network.addConnection(self.HDFsource.getOutport('outport'), HDFvolume_list[i][0].getInport('inport'))
                self.network.addConnection(self.HDFsource.getOutport('outport'), HDFvolume_list[i][1].getInport('inport'))
                self.network.addConnection(HDFvolume_list[i][0].getOutport('outport'), HDFvolume_list[i][2].getInport('inport'))
                self.network.addConnection(HDFvolume_list[i][1].getOutport('outport'), HDFvolume_list[i][2].getInport('inport'))
                
                if merger_list:
                    if ((i+1) % 4) == 1:
                        self.network.addConnection(HDFvolume_list[i][2].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('inputVolume'))
                    else:
                        self.network.addConnection(HDFvolume_list[i][2].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('volume'+str((i%4)+1)))

        # Set hdf5 path properties

        scaling_factor = 1
        # Read base vectors and extract scaling factor
        with h5py.File(self.hdf5_path, "r") as h5:
            basis_4x4=np.identity(4)
            basis_array=np.array(h5["/basis/"], dtype='d')
            basis_4x4[:3,:3]=basis_array
            scaling_factor = h5['/scaling_factor'].value

        minValue = inviwopy.glm.mat4(-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000,
                                    -1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000)
        maxValue = inviwopy.glm.mat4(1000,1000,1000,1000,1000,1000,1000,1000,
                                    1000,1000,1000,1000,1000,1000,1000,1000)
        scaling_matrix = inviwopy.glm.mat4(scaling_factor * basis_4x4[0][0],scaling_factor * basis_4x4[0][1],scaling_factor * basis_4x4[0][2],
                                scaling_factor * basis_4x4[0][3],scaling_factor * basis_4x4[1][0],scaling_factor * basis_4x4[1][1],
                                scaling_factor * basis_4x4[1][2],scaling_factor * basis_4x4[1][3],scaling_factor * basis_4x4[2][0],
                                scaling_factor * basis_4x4[2][1],scaling_factor * basis_4x4[2][2],scaling_factor * basis_4x4[2][3],
                                scaling_factor * basis_4x4[3][0],scaling_factor * basis_4x4[3][1],scaling_factor * basis_4x4[3][2],
                                scaling_factor * basis_4x4[3][3])
        
        for i in range(0, n_bands):
            if mode_list[i] == 0 or mode_list[i] == 1:
                hdfvolume_volumeSelection_property = HDFvolume_list[i].getPropertyByIdentifier('volumeSelection')       
                hdfvolume_volumeSelection_property.selectedValue = '/PARCHG/Bands/' + str(band_list[i]) + '/' + mode_dict[mode_list[i]] 
                HDFvolume_basis_property = HDFvolume_list[i].getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')

            else:
                hdfvolume_volumeSelection_property = HDFvolume_list[i][0].getPropertyByIdentifier('volumeSelection')
                hdfvolume_volumeSelection_property.selectedValue = '/PARCHG/Bands/' + str(band_list[i]) + '/' + mode_dict[0]
                HDFvolume_basis_property = HDFvolume_list[i][0].getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')

                hdfvolume_volumeSelection_property = HDFvolume_list[i][1].getPropertyByIdentifier('volumeSelection')
                hdfvolume_volumeSelection_property.selectedValue = '/PARCHG/Bands/' + str(band_list[i]) + '/' + mode_dict[1]
                HDFvolume_basis_property = HDFvolume_list[i][1].getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')

            HDFvolume_basis_property.minValue = minValue
            HDFvolume_basis_property.maxValue = maxValue
            HDFvolume_basis_property.value = scaling_matrix

        # Connect volume mergers and save the resulting outport 
        if not merger_list:
            volumeOutport = HDFvolume_list[0].getOutport('outport')
        else:
            for i in range(0, len(merger_list)):
                if (i + 1) != len(merger_list):
                    for j in range(0, len(merger_list[i])):
                        if ((j+1) % 4) == 1:
                            self.network.addConnection(merger_list[i][j].getOutport('outputVolume'), merger_list[i+1][math.floor(j/4)].getInport('inputVolume'))
                        else:
                            self.network.addConnection(merger_list[i][j].getOutport('outputVolume'), merger_list[i+1][math.floor(j/4)].getInport('volume'+str((j%4)+1)))
            
            volumeOutport = merger_list[-1][0].getOutport('outputVolume')

        self.connect_volume(volumeOutport)


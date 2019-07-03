#
#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys,os,inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py

from VolumeNetworkHandler import VolumeNetworkHandler
from UnitcellNetworkHandler import UnitcellNetworkHandler

class ELFNetworkHandler(VolumeNetworkHandler, UnitcellNetworkHandler):
    """ Handler class for ELF visualization self.network.
        Sets up and manages the ELF visualization
    """
    def __init__(self, hdf5_path, inviwoApp):
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
            if file.get("ELF") == None:
                raise AssertionError("No ELF data in that file")
        if len(self.get_available_bands(hdf5_path)) == 0:
            raise AssertionError("No valid bands in that file")
        
        # Setup default ELF settings
        self.setup_ELF_network(hdf5_path)
        self.set_active_band('final')

        # Setup default unitcell settings
        if self.unitcellAvailable:
            self.toggle_full_mesh(False)
            self.toggle_unitcell_canvas(False)
    
    def get_available_bands(self, path):
    # Return the keys to the available datasets in hdf5-file
        with h5py.File(path, 'r') as file:
            band_keys = []
            for key in file.get("ELF").keys():
                band_keys.append(key)
            return band_keys

# ------------------------------------------
# ------- Property control functions -------
    
    def set_active_band(self, key):
    # Sets the dataset which HDF5 to volume processor will read
        
        toVolume = self.network.getProcessorByIdentifier('HDF5 To Volume')
        toVolume.volumeSelection.selectedValue = '/ELF/' + key

    def position_canvases(self, x, y):
    # Updates the position of the canvases
    # Upper left corner will be at coordinate (x, y)
        
        sliceCanvas = self.network.getProcessorByIdentifier('SliceCanvas')
        volumeCanvas = self.network.getProcessorByIdentifier('Canvas')
        unitcellCanvas = self.network.getProcessorByIdentifier('Unit Cell Canvas')
        if not volumeCanvas:
            return
        volumeCanvas.position.value = inviwopy.glm.ivec2(x, y)
        if sliceCanvas:
            sliceCanvas.position.value = inviwopy.glm.ivec2(x, y + volumeCanvas.inputSize.dimensions.value.y + 50)
        if unitcellCanvas:
            unitcellCanvas.position.value = inviwopy.glm.ivec2(x + volumeCanvas.inputSize.dimensions.value.x, y)

# ------------------------------------------
# ------- Network building functions -------

    def setup_ELF_network(self, hdf5_path):
    # Setup the part of the inviwo self.network which handles hdf5 to volume conversion*
        
        
        xstart_pos = 0
        ystart_pos = 0

        # Add the "HDF Source" processor to inviwo self.network
        HDFsource = self.add_h5source(hdf5_path, xstart_pos, ystart_pos)
        HDFsource.filename.value = hdf5_path

        # Hdf5 to volume converter processor
        HDFvolume = self.add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 To Volume', xstart_pos, ystart_pos+75)

        # Read base vectors
        with h5py.File(hdf5_path, "r") as h5:
            basis_4x4=np.identity(4)
            basis_array=np.array(h5["/basis/"], dtype='d')
            basis_4x4[:3,:3]=basis_array
            scaling_factor = h5['/scaling_factor'].value

        HDFvolume_basis_property = HDFvolume.getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')
        HDFvolume_basis_property.minValue = inviwopy.glm.mat4(-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000,
                                                            -1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000)
        HDFvolume_basis_property.maxValue = inviwopy.glm.mat4(1000,1000,1000,1000,1000,1000,1000,1000,
                                                            1000,1000,1000,1000,1000,1000,1000,1000)
        HDFvolume_basis_property.value = inviwopy.glm.mat4(scaling_factor * basis_4x4[0][0],scaling_factor * basis_4x4[0][1],scaling_factor * basis_4x4[0][2],
                                                        scaling_factor * basis_4x4[0][3],scaling_factor * basis_4x4[1][0],scaling_factor * basis_4x4[1][1],
                                                        scaling_factor * basis_4x4[1][2],scaling_factor * basis_4x4[1][3],scaling_factor * basis_4x4[2][0],
                                                        scaling_factor * basis_4x4[2][1],scaling_factor * basis_4x4[2][2],scaling_factor * basis_4x4[2][3],
                                                        scaling_factor * basis_4x4[3][0],scaling_factor * basis_4x4[3][1],scaling_factor * basis_4x4[3][2],
                                                        scaling_factor * basis_4x4[3][3])
        
        self.network.addConnection(HDFsource.getOutport('outport'), HDFvolume.getInport('inport'))
        
        self.connect_volume(HDFvolume.getOutport('outport'))

        # Connect unitcell and volume visualisation.
        volumeBoxRenderer = self.network.getProcessorByIdentifier('Mesh Renderer')
        unitcellRenderer = self.network.getProcessorByIdentifier('Unit Cell Renderer')
        if volumeBoxRenderer and unitcellRenderer:
            self.network.addConnection(unitcellRenderer.getOutport('image'), volumeBoxRenderer.getInport('imageInport'))
            self.network.addLink(unitcellRenderer.getPropertyByIdentifier('camera'), volumeBoxRenderer.getPropertyByIdentifier('camera'))
            self.network.addLink(volumeBoxRenderer.getPropertyByIdentifier('camera'), unitcellRenderer.getPropertyByIdentifier('camera'))
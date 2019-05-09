

import sys,os,inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py
from common import _add_h5source, _add_processor

from VolumeNetworkHandler import VolumeNetworkHandler

class ChargeNetworkHandler(VolumeNetworkHandler):
    """ Base class for setting up and handling a network for generic volume rendering for ENVISIoN.
    Need to be supplied with outports of volume data from somewhere.
    Not used directly, is inherited in other classes for handling specific visualizations


    """
    def __init__(self, hdf5_path):
        super().__init__() # Will setup generic part of network

        self.setup_volume_source(hdf5_path)
        

    def setup_volume_source(self, hdf5_path):
    # Setup the part of the inviwo network which handles hdf5 to volume conversion*
        network = inviwopy.app.network
        
        xstart_pos = 0
        ystart_pos = 0

        # Add the "HDF Source" processor to inviwo network
        HDFsource = _add_h5source(hdf5_path, xstart_pos, ystart_pos)
        HDFsource.filename.value = hdf5_path

        # Hdf5 to volume converter processor
        HDFvolume = _add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 To Volume', xstart_pos, ystart_pos+75)

        # Read base vectors
        with h5py.File(hdf5_path, "r") as h5:
            basis_4x4=np.identity(4)
            basis_array=np.array(h5["/basis/"], dtype='d')
            basis_4x4[:3,:3]=basis_array
            scaling_factor = h5['/scaling_factor'].value

        # Set correct path to volume data
        hdfvolume_volumeSelection_property = HDFvolume.getPropertyByIdentifier('volumeSelection')
        hdfvolume_volumeSelection_property.value = '/CHG/final' 

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
        
        network.addConnection(HDFsource.getOutport('outport'), HDFvolume.getInport('inport'))
        
        self.connect_volume(HDFvolume.getOutport('outport'))
        self.connect_volume(HDFvolume.getOutport('outport'))
        self.connect_volume(HDFvolume.getOutport('outport'))
        self.connect_volume(HDFvolume.getOutport('outport'))
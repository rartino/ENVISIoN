#
#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
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
from common import _add_h5source, _add_processor

from VolumeNetworkHandler import VolumeNetworkHandler

# TODO: Add check to make sure path is valid

class ChargeNetworkHandler(VolumeNetworkHandler):
    """ Handler class for charge visualization network.
        Sets up and manages the charge visualization
    """
    def __init__(self, hdf5_path):
        super().__init__() # Will setup generic part of network

        self.setup_volume_source(hdf5_path)
        # self.clear_tf()
        self.toggle_slice_canvas(False)
        self.set_plane_normal()
        self.set_slice_background(inviwopy.glm.vec4(0,0,0,1),
                            inviwopy.glm.vec4(1,1,1,1),3,0)
        self.slice_copy_tf()
        

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
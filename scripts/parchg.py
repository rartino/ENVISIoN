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

import os, sys, inspect, inviwopy

path_to_envisionpy = "/home/labb/ENVISIoN"
sys.path.append(path_to_envisionpy)
import envisionpy
import envisionpy.hdf5parser
from envisionpy.processor_network.ParchgNetworkHandler import ParchgNetworkHandler

# Set the path to existing VASP directory and to the desired save location for HDF5-file.
PATH_TO_VASP_CALC=os.path.expanduser("/home/labb/VASP_files/diamond_partial_charges/partial_charges")
PATH_TO_HDF5=os.path.expanduser("/home/labb/HDF5_new/pachg_demo.hdf5")

# Parse for charge density visualisation.
envisionpy.hdf5parser.parchg(PATH_TO_HDF5, PATH_TO_VASP_CALC)
envisionpy.hdf5parser.unitcell(PATH_TO_HDF5, PATH_TO_VASP_CALC)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
networkHandler = ParchgNetworkHandler(PATH_TO_HDF5, inviwopy.app)

# Set band selections and modes
# band_list : list of the bands you want to visualize, by number, e.g. [34,55,190] to select band 34, 55 and 190
# mode_list : Specifies how to visualize a specific band. In the order you enumerated your bands in parchg_list, choose mode where
#    0 for 'total'
#    1 for 'magnetic'
#    2 for 'up'
#    3 for 'down'
# Example: If band_list is [31, 212] and mode_list is [1,3], band 31 will be visualized as 'magnetic' and 212 as 'down'
band_list = [1, 2, 3, 4]
mode_list = [0, 0, 0, 0]
networkHandler.select_bands(band_list, mode_list)

# Set some default properties, everything can either be 
# chaged via networkHandler class or directly in
# the network editor

# Add some default transfer function points
# networkHandler.clear_tf()
# networkHandler.add_tf_point(0.45, inviwopy.glm.vec4(1, 1, 1, 0))
# networkHandler.add_tf_point(0.5, inviwopy.glm.vec4(0.1, 1, 0.1, 0.1))

# Configure slice visualisation
networkHandler.toggle_slice_canvas(False)
networkHandler.toggle_slice_plane(False)
networkHandler.set_plane_normal(0, 1, 0)
networkHandler.set_plane_height(0.5)

# Configure unitcell visualisation
if networkHandler.unitcellAvailable:
    networkHandler.toggle_unitcell_canvas(True)
    networkHandler.set_atom_radius(0.2)


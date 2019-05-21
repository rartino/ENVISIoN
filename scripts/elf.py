#
#  ENVISIoN
#
#  Copyright (c) 2018 Viktor Bernholtz
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
#  Alterations to this file by Viktor Bernholtz, Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import os, sys, inspect, inviwopy
path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir + "/../envision"))
import envision
from envision.inviwo.ELFNetworkHandler import ELFNetworkHandler

# Set the path to existing VASP directory and to the desired save location for HDF5-file.
PATH_TO_VASP_CALC=os.path.expanduser("C:/Kandidatprojekt/VASP/TiPO4_ELF")
PATH_TO_HDF5=os.path.expanduser("C:/Kandidatprojekt/HDF5/elf_demo.hdf5")

# Parse for charge density visualisation.
envision.parser.vasp.elf(PATH_TO_HDF5, PATH_TO_VASP_CALC)
try:
    envision.parser.vasp.unitcell(PATH_TO_HDF5, PATH_TO_VASP_CALC)
except Exception as error:
    print(error)

# Clear any old network
inviwopy.app.network.clear()

# Initialize inviwo network
networkHandler = ELFNetworkHandler(PATH_TO_HDF5)

# Set some default properties, everything can either be 
# chaged via networkHandler class or directly in
# the network editor

# Add some default transfer function points
networkHandler.add_tf_point(0.45, inviwopy.glm.vec4(1, 1, 1, 0))
networkHandler.add_tf_point(0.5, inviwopy.glm.vec4(0.1, 1, 0.1, 0.1))

# Configure slice visualisation
networkHandler.toggle_slice_canvas(True)
networkHandler.toggle_slice_plane(True)
networkHandler.set_plane_normal(0, 1, 0)
networkHandler.set_plane_height(0.5)

# Configure unitcell visualisation
if networkHandler.unitcellAvailable:
    networkHandler.hide_atoms(False)
    networkHandler.toggle_unitcell_canvas(True)
    networkHandler.set_atom_radius(0.2)


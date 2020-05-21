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

# HDF5 FILES

# "/BCC/Cu_unit_BCC.hdf5"
# "/CUB/Cu_unit_CUB.hdf5"
# "/FCC/Cu_unit_FCC.hdf5"
# "/FCC/NaCl_unit_FCC.hdf5"
# "/HEX/C_unit_HEX.hdf5"
# "/HEX/SIOX_unit_HEX.hdf5"
# "/ORC/BaSO4_unit_ORC.hdf5"
# "/ORC/FeS2_unit_ORC.hdf5"
# "/TET/TiO2_unit_TET.hdf5"
# "/TRI/P2I4_unit_TRI_a.hdf5"
# "/TRI/P2I4_unit_TRI_b.hdf5"

# CONFIGURE FILE PATHS HERE

# Path to your envision installation
PATH_TO_ENVISION = "/home/labb/ENVISIoN/ENVISIoN"

# Path to the folder of the HDF5 files you want to use 
PATH_TO_HDF5 = PATH_TO_ENVISION + "/data_HDF5/Enhetsceller_HDF5"

# Path to the HDF5 file you want to use
HDF5_FILE = "/ORC/BaSO4_unit_ORC.hdf5"

import os, sys, inspect, inviwopy
sys.path.append(PATH_TO_ENVISION)
import envisionpy
from envisionpy.processor_network.UnitcellNetworkHandler import UnitcellNetworkHandler

# Initialize inviwo network

inviwopy.app.network.clear()
networkHandler = UnitcellNetworkHandler(PATH_TO_HDF5, inviwopy.app)


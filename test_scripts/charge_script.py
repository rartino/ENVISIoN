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

# "/CUB/Cu_charge_CUB.hdf5"
# "/FCC/NaCl_charge_FCC.hdf5"
# "/HEX/C_charge_HEX.hdf5"
# "/ORC/BaSO4_charge_ORC.hdf5"

# CONFIGURE FILE PATHS HERE

# Path to your envision installation
PATH_TO_ENVISION = "/home/labb/ENVISIoN/ENVISIoN"

# Path to the folder of the HDF5 files you want to use 
PATH_TO_HDF5 = PATH_TO_ENVISION + "/data_HDF5/Elektrontathet_HDF5"

# Path to the HDF5 file you want to use
HDF5_FILE = "/ORC/BaSO4_charge_ORC.hdf5"

import os, sys, inspect, inviwopy
sys.path.append(PATH_TO_ENVISION)
import envisionpy
from envisionpy.processor_network.ChargeNetworkHandler import ChargeNetworkHandler
from envisionpy.processor_network.VolumeNetworkHandler import VolumeNetworkHandler

# Initialize inviwo network

inviwopy.app.network.clear()
networkHandler = ChargeNetworkHandler(PATH_TO_HDF5, inviwopy.app)
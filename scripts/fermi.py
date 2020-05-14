#  ENVISIoN
#
#  Copyright (c) 2020 Alexander Vevstad
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

# CONFIGURE FILE PATHS HERE

# Path to your envision installation
PATH_TO_ENVISION = "/home/docker/ENVISIoN/ENVISIoN"

# Path to the vasp output directory you wish to visualise
PATH_TO_VASP_CALC = "/home/docker/ENVISIoN/data/FCC-Cu"

# Path to where you want to save the resulting hdf5 file
PATH_TO_HDF5 = "/home/docker/ENVISIoN/demo.h5"

import os, sys, inspect

sys.path.append(PATH_TO_ENVISION)

import inviwopy
import inviwopy.glm as glm

import envisionpy
import envisionpy.hdf5parser
from envisionpy.processor_network.FermiSurfaceNetworkHandler import FermiSurfaceNetworkHandler

envisionpy.hdf5parser.fermi_parser(PATH_TO_HDF5, PATH_TO_VASP_CALC)

app = inviwopy.app
app.network.clear()
networkHandler = FermiSurfaceNetworkHandler(PATH_TO_HDF5, app)

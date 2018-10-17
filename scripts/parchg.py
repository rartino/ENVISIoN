#
#  ENVISIoN
#
#  Copyright (c) 2018 Elvis Jakobsson
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


import os, sys

# Configuration
PATH_TO_ENVISION=os.path.expanduser("~/PROJLAB/ENVISIoN/envision")
PATH_TO_VASP_CALC=os.path.expanduser("~/PROJLAB/ENVISIoN/data/diamond")
PATH_TO_HDF5=os.path.expanduser("~/Desktop/demo.hdf5")

sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION))

import envision
import envision.inviwo

#Inarguments to inviwo.parchg:
#--------------------------------
#Path to your HDF5 file
#sli : True for slice function, False for no slice function
#parchg_list : list of the bands you want to visualize, by number, e.g. [34,55,190] for band 34, 55 and 190
#parchg_mode : Determines how the datasets are visualized. Options are:
#    - 'total' : spin_up + spin_down
#    - 'magnetic' : spin_up - spin_down
#    - 'up' : spin_up (0.5*(total+magnetic))
#    - 'down' : spin_down (0.5*(total-magnetic))
#    - 'mixed' : allows a specific mode for individual bands. If this is picked, you are required to fill out the mode_list.
#mode_list : Specifies how to visualize a specific band. In the order you enumerated your bands in parchg_list, choose mode where
#    0 for 'total'
#    1 for 'magnetic'
#    2 for 'up'
#    3 for 'down'
#    Example: If parchg_list is [31, 212] and mode_list is [1,3], band 31 will be visualized as 'magnetic' and 212 as 'down'
#xstart_pos : where you want the Inviwo circuit to start on the x-axis
#ystart_pos : where you want the Inviwo circuit to start on the y-axis


envision.parser.vasp.unitcell(PATH_TO_HDF5, PATH_TO_VASP_CALC)
envision.parser.vasp.parchg(PATH_TO_HDF5, PATH_TO_VASP_CALC)

envision.inviwo.unitcell(PATH_TO_HDF5, xpos = 0, ypos = 0, smallAtoms = True)
envision.inviwo.parchg(PATH_TO_HDF5, sli = False, parchg_list = [1,2,3,4], parchg_mode = 'total', mode_list = [0,1,2,3], xstart_pos = 600, ystart_pos = 0)

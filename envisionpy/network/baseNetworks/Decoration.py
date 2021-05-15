##  ENVISIoN
##
##  Copyright (c) 2021 Gabriel Anderberg, Didrik Axén,  Adam Engman,
##  Kristoffer Gubberud Maras, Joakim Stenborg
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice, this
##  list of conditions and the following disclaimer.
##  2. Redistributions in binary form must reproduce the above copyright notice,
##  this list of conditions and the following disclaimer in the documentation
##  and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
##  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## ##############################################################################################

import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork

class Decoration(Subnetwork):
    '''
    Base decoration class
    '''
    def __init__(self, inviwoApp):
        Subnetwork.__init__(self, inviwoApp)
        self.other_subnetworks = {}
        self.force_enabled = True;
        #self.force_enabled = False

    def __del__(self):
        # Disconnect this from other networks.
        for vis_type, subnetwork in self.other_subnetworks.items():
            self.disconnect_decoration(subnetwork, vis_type)


    # Should be overloaded in inheritor class
    def valid_visualisations(self):
        return []

    # Should be overloaded in inheritor class
    def connect_decoration(self, other, vis_type):
        if vis_type not in self.valid_visualisations():
            raise EnvisionError('Invalid visualisation type ['+vis_type+'].')
        self.other_subnetworks[vis_type] = other

    # Should be overloaded in inheritor class
    def disconnect_decoration(self, other, vis_type):
        pass
    #Skissat från toggle_iso i VolumeSubnetwork.py rad 164
    def disable_force(self, enable):
        if enable:
            self.force_enabled = False
        else:
            self.force_enabled = True

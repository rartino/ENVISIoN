#
#  ENVISIoN
#
#  Copyright (c) 2019 Anton Hjert
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

import wx, sys, os, h5py
from generalCollapsible import GeneralCollapsible
from volumeControlCollapsible import VolumeControlCollapsible
from backgroundCollapsible import BackgroundCollapsible
from sliceControlCollapsible import SliceControlCollapsible
import envision

from envision.inviwo.ChargeNetworkHandler import ChargeNetworkHandler

class ChargeFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, label = "Charge")
        self.slice=False

        # Setup volume rendering controls
        self.volumeCollapsible = VolumeControlCollapsible(self.GetPane(), "Volume Rendering")
        self.add_sub_collapsible(self.volumeCollapsible)

        # Setup background controls
        self.backgroundCollapsibe = BackgroundCollapsible(self.GetPane(), "Background")
        self.add_sub_collapsible(self.backgroundCollapsibe)
        
        #Setup slice-checkbox
        self.sliceBox = wx.CheckBox(self.GetPane(), label="Slice")
        self.add_item(self.sliceBox)
        
        # Setup slice controls
        self.sliceCollapsible = SliceControlCollapsible(self.GetPane(), "Volume Slice")
        self.add_sub_collapsible(self.sliceCollapsible)

        # self.hide_sub_collapsible(3)

        # Override default binding
        # Note that function should be called "on_collapse" to work
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)
        self.sliceBox.Bind(wx.EVT_CHECKBOX,self.on_check)

    def on_check(self,event):
        self.networkHandler.toggle_slice_canvas(event.IsChecked())
        self.networkHandler.toggle_slice_plane(event.IsChecked())
        # if self.slice:
        #     self.slice = False
        #     self.backgroundCollapsibe.type = 'Background'
        #     self.backgroundCollapsibe.SetLabel('Background')
        #     self.hide_sub_collapsible(3)
        # else:
        #     self.slice = True
        #     self.show_sub_collapsible(3)
        #     self.backgroundCollapsibe.SetLabel('Volume background')
        #     self.backgroundCollapsibe.type = 'VolumeBackground'
        #     self.sliceCollapsible.Collapse(False)
        # self.update_collapse()
        # self.start_vis()

    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable charge vis
            del self.networkHandler
        else:
            # Initialize network handler which starts visualization
            self.networkHandler = ChargeNetworkHandler(self.parent_collapsible.path)
            self.volumeCollapsible.networkHandler = self.networkHandler
            self.sliceCollapsible.networkHandler = self.networkHandler
            self.backgroundCollapsibe.networkHandler = self.networkHandler
            
    
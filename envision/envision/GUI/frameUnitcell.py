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
#  Alterations to this file by
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
import wx ,sys ,os , h5py
from parameter_utils import *
from generalCollapsible import GeneralCollapsible

class UnitcellFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Unitcell")
    
        button1 = wx.Button(self.GetPane(), label="X")
        button2 = wx.Button(self.GetPane(), label="Y")
        slider = wx.Slider(self.GetPane())

        self.add_item(button1)
        self.add_item(button2)
        self.add_item(slider)

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    
    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable Unitcell vis
            clear_processor_network()
            print("Not Unitcell")
        else:
            self.start_vis()

    def start_vis(self):
        if self.isPathEmpty():
            return
        elif "/UnitCell" in  h5py.File(self.parent_collapsible.path, 'r'):
            #Start Unitcell vis
            envision.inviwo.unitcell(self.parent_collapsible.path, 
                                    xpos = 0, ypos = 0)
            self.set_canvas_pos('Unitcell')
            print("Unitcell")
        else:
            self.open_message('The file of choice does not contain Unitcell-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()


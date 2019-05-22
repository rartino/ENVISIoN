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
from UnitcellCollapsible import UnitcellCollapsible
import envision
import inviwopy

from envision.inviwo.UnitcellNetworkHandler import UnitcellNetworkHandler

class UnitcellFrame(UnitcellCollapsible):
    def __init__(self, parent):
        UnitcellCollapsible.__init__(self, parent, label="Unitcell")

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    
    def on_collapse(self, event=None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.isPathEmpty():
            return
        if not self.IsCollapsed():
            # Initialize network handler which starts visualization
            # Exception caught if hdf5 file is not valid
            try:
                self.networkHandler = UnitcellNetworkHandler(self.parent_collapsible.path)
            except AssertionError as error:
                print(error)
                inviwopy.app.network.clear()
                self.Collapse(True)
                self.update_collapse()
                self.open_message(str(error), "Cannot start visualization")
                return

            self.hasAtoms = False
            for i in range(self.networkHandler.nAtomTypes):
                self.add_atom_control(self.networkHandler.get_atom_name(i), i)

            self.reset_canvas_position()

        elif self.networkHandler:
            # Disable charge visualization
            self.networkHandler.clear_processor_network()
            del self.networkHandler

    def reset_canvas_position(self):
        window = self.GetTopLevelParent()
        self.networkHandler.set_canvas_position(window.GetPosition().x + window.GetSize().width, window.GetPosition().y)


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
from UnitcellCollapsible import UnitcellCollapsible
import envision
import inviwopy

from envision.inviwo.ELFNetworkHandler import ELFNetworkHandler

class ELFFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, label = "ELF")

        # Setup band selector choice box
        bandChoiceLabel = wx.StaticText(self.GetPane(), label="Select band: ")
        bandChoiceLabel.SetToolTip(
            "Choose what band to visualize")

        self.bandChoice = wx.Choice(self.GetPane())

        bandChoiceHBox = wx.BoxSizer(wx.HORIZONTAL)
        bandChoiceHBox.Add(bandChoiceLabel)
        bandChoiceHBox.Add(self.bandChoice)
        self.add_item(bandChoiceHBox)

        # Setup unicell checkbox
        self.spheresCheckbox = wx.CheckBox(self.GetPane(), label="Enable atom spheres")
        self.spheresCheckbox.SetValue(True)
        self.add_item(self.spheresCheckbox)

        self.unitcellCheckbox = wx.CheckBox(self.GetPane(), label="Enable separate unitcell canvas")
        self.unitcellCheckbox.SetValue(False)
        self.add_item(self.unitcellCheckbox)

        #Setup slice-checkbox
        self.sliceBox = wx.CheckBox(self.GetPane(), label="Enable volume slice")
        self.add_item(self.sliceBox)

        # Setup volume rendering controls
        self.volumeCollapsible = VolumeControlCollapsible(self.GetPane(), "Volume Rendering")
        self.add_sub_collapsible(self.volumeCollapsible)

        # Unitcell collapsible
        self.unitcellCollapsible = UnitcellCollapsible(self.GetPane())
        self.add_sub_collapsible(self.unitcellCollapsible)

        # Setup background controls
        self.backgroundCollapsibe = BackgroundCollapsible(self.GetPane(), "Background")
        self.add_sub_collapsible(self.backgroundCollapsibe)
        
        # Setup slice controls
        self.sliceCollapsible = SliceControlCollapsible(self.GetPane(), "Volume Slice")
        self.add_sub_collapsible(self.sliceCollapsible)

        # self.hide_sub_collapsible(3)

        # Override default binding
        # Note that function should be called "on_collapse" to work
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)
        self.spheresCheckbox.Bind(wx.EVT_CHECKBOX, self.on_sphere_check)
        self.unitcellCheckbox.Bind(wx.EVT_CHECKBOX,self.on_unitcell_check)
        self.sliceBox.Bind(wx.EVT_CHECKBOX,self.on_slice_check)
        self.bandChoice.Bind(wx.EVT_CHOICE, self.on_band_selection)

    def on_slice_check(self,event):
        self.networkHandler.toggle_slice_canvas(event.IsChecked())
        self.networkHandler.toggle_slice_plane(event.IsChecked())
        self.reset_canvas_positions()

    def on_sphere_check(self, event):
    # Event when sphere checkbox is clicked
        if self.networkHandler.unitcellAvailable:
            self.networkHandler.hide_atoms(not event.IsChecked())

    def on_unitcell_check(self, event):
    # Event when unitcell checkbox is clicked
        if self.networkHandler.unitcellAvailable:
            self.networkHandler.toggle_unitcell_canvas(event.IsChecked()) 
            self.reset_canvas_positions()

    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.isPathEmpty():
            return
        
        if not self.IsCollapsed():
            # Initialize network handler which starts visualization
            # Exception caught if hdf5 file is not valid
            try:
                self.networkHandler = ELFNetworkHandler(self.parent_collapsible.path)
            except AssertionError as error:
                print(error)
                inviwopy.app.network.clear()
                self.Collapse(True)
                self.update_collapse()
                self.open_message(str(error), "Cannot start visualization")
                return

            # Set the Network Handler of everyone that needs it
            self.volumeCollapsible.networkHandler = self.networkHandler
            self.sliceCollapsible.networkHandler = self.networkHandler
            self.sliceCollapsible.sliceBackgroundCollapsibe.networkHandler = self.networkHandler
            self.backgroundCollapsibe.networkHandler = self.networkHandler
            self.unitcellCollapsible.networkHandler = self.networkHandler

            self.unitcellCollapsible.hasAtoms = False
            if self.networkHandler.unitcellAvailable:
                for i in range(self.networkHandler.nAtomTypes):
                    self.unitcellCollapsible.add_atom_control(self.networkHandler.get_atom_name(i), i)

            # Add a default tf-point, just so volume is not empty on startup
            self.volumeCollapsible.add_tf_point(0.5, 0.1, wx.Colour(20, 200, 20, 20))
            self.volumeCollapsible.re_read_tf_points()

            # Set canvases to appear next to window
            self.reset_canvas_positions()

            # Load band choices
            self.bandChoice.Clear()
            for key in self.networkHandler.get_available_bands(self.parent_collapsible.path):
                self.bandChoice.Append(key)
                self.bandChoice.SetSelection(self.bandChoice.FindString('final'))

            # Check if unitcell is available
            self.spheresCheckbox.SetValue(self.networkHandler.unitcellAvailable)
            self.spheresCheckbox.Enable(self.networkHandler.unitcellAvailable)
            self.unitcellCheckbox.Enable(self.networkHandler.unitcellAvailable)
            if not self.networkHandler.unitcellAvailable:
                self.spheresCheckbox.SetToolTip("No unitcell parsed into HDF5 file.")
                self.unitcellCheckbox.SetToolTip("No unitcell parsed into HDF5 file.")
            else:
                self.spheresCheckbox.SetToolTip("")
                self.unitcellCheckbox.SetToolTip("")

        elif self.networkHandler:
            # Disable charge visualization
            self.networkHandler.clear_processor_network()
            del self.networkHandler

    def on_band_selection(self, event):
        self.networkHandler.set_active_band(event.GetString())


    def reset_canvas_positions(self):
        window = self.GetTopLevelParent()
        self.networkHandler.position_canvases(window.GetPosition().x + window.GetSize().width, window.GetPosition().y)
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
import wx
import inviwopy
from generalCollapsible import GeneralCollapsible
from volumeControlCollapsible import VolumeControlCollapsible
from backgroundCollapsible import BackgroundCollapsible
from sliceControlCollapsible import SliceControlCollapsible
from UnitcellCollapsible import UnitcellCollapsible

from envision.inviwo.ParchgNetworkHandler import ParchgNetworkHandler

class ParchgFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Partial Charge")
        



        # Setup band chooser choise box
        bandChoiceLabel = wx.StaticText(self.GetPane(), label="Select bands: ")
        bandChoiceLabel.SetToolTip(
            "Choose which bands to visualize")
        self.add_item(bandChoiceLabel)


        # List containing the band selector widgets
        self.selectorWidgets = []

        # List of possible band choices, fills up based on selected hdf5 file
        self.bandChoices = ['None']
        
        # Initialize the first band selector widget
        bandSelector = BandSelectorWidget(self.GetPane(), self.bandChoices)
        self.selectorWidgets.append(bandSelector)
        
        bandSelector.bandChooser.Bind(wx.EVT_CHOICE, lambda event : self.band_selection_changed(bandSelector))

        # Add stuff to sizer
        self.selectorVBox = wx.BoxSizer(wx.VERTICAL)
        self.selectorVBox.Add(bandSelector)

        self.add_item(self.selectorVBox)


        # Add unicell controls
        self.spheresCheckbox = wx.CheckBox(self.GetPane(), label="Enable atom spheres")
        self.spheresCheckbox.SetValue(True)
        self.add_item(self.spheresCheckbox)

        # Add slice-checkbox
        self.sliceBox = wx.CheckBox(self.GetPane(), label="Enable volume slice")
        self.add_item(self.sliceBox)

        # Add volume rendering collapsible
        self.volumeCollapsible = VolumeControlCollapsible(self.GetPane(), "Volume Rendering")
        self.add_sub_collapsible(self.volumeCollapsible)

        # Add slice collapsible
        self.sliceCollapsible = SliceControlCollapsible(self.GetPane(), "Volume Slice")
        self.add_sub_collapsible(self.sliceCollapsible)

        # Unitcell collapsible
        self.unitcellCollapsible = UnitcellCollapsible(self.GetPane())
        self.add_sub_collapsible(self.unitcellCollapsible)

        # Setup background controls
        self.backgroundCollapsibe = BackgroundCollapsible(self.GetPane(), "Background")
        self.add_sub_collapsible(self.backgroundCollapsibe)

        # Bind events
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)
        self.spheresCheckbox.Bind(wx.EVT_CHECKBOX, self.on_sphere_check)
        self.sliceBox.Bind(wx.EVT_CHECKBOX,self.on_slice_check)

    def band_selection_changed(self, selectorWidget):
    # Handle input to band selection widgets
        selectedString = selectorWidget.bandChooser.GetString(selectorWidget.bandChooser.GetSelection())

        if len(self.selectorWidgets) > 1 and selectedString == 'None':
        # If none selected and its not the last widget, remove widget
            selectorWidget.Clear(delete_windows = True)
            self.selectorWidgets.remove(selectorWidget)
            self.selectorVBox.Remove(selectorWidget)
        
        elif selectedString != 'None' and selectorWidget.activeBand == None:
        # Selection was changed from None to some number.
            selectorWidget.activeBand = selectorWidget.bandChooser.GetSelection()
            # Add new selection widged with None as selection
            newBandSelector = BandSelectorWidget(self.GetPane(), self.bandChoices)
            newBandSelector.bandChooser.Bind(wx.EVT_CHOICE, lambda event : self.band_selection_changed(newBandSelector))
            self.selectorVBox.Add(newBandSelector)
            self.selectorWidgets.append(newBandSelector)

        elif selectedString != 'None':
        # Selection was changed from one number to another.
            pass

        self.reload_band_processors()
        self.update_collapse()
    

        self.update_collapse()

    def on_slice_check(self,event):
        self.networkHandler.toggle_slice_canvas(event.IsChecked())
        self.networkHandler.toggle_slice_plane(event.IsChecked())
        self.reset_canvas_positions()

    def on_sphere_check(self, event):
    # Event when sphere checkbox is clicked
        if self.networkHandler.unitcellAvailable:
            self.networkHandler.hide_atoms(not event.IsChecked())

    def reload_band_processors(self):
    # Reload the inviwo band processors with the specified selections
        bandList = []
        modeList = []
        for widget in self.selectorWidgets:
            if widget.bandChooser.GetSelection() == 0:
                continue
            try:
                bandList.append(widget.bandChooser.GetString(widget.bandChooser.GetSelection()))
                modeList.append(widget.modeChooser.GetSelection())
            except ValueError:
                continue
        self.networkHandler.select_bands(bandList, modeList)
            
    def on_collapse(self, event = None):
        self.update_collapse()

        if self.isPathEmpty():
            return

        if not self.IsCollapsed():
            # Initialize network handler which starts visualization
            # Exception caught if hdf5 file is not valid
            try:
                self.networkHandler = ParchgNetworkHandler(self.parent_collapsible.path, [], [])
            except AssertionError as error:
                print(error)
                inviwopy.app.network.clear()
                self.Collapse(True)
                self.update_collapse()
                self.open_message(str(error), "Cannot start visualization")
                return

            self.bandChoices = ['None'] + self.networkHandler.get_available_bands(self.parent_collapsible.path)
            for w in self.selectorWidgets:
                w.bandChooser.Clear()
                w.bandChooser.AppendItems(self.bandChoices)

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

            # Check if unitcell is available
            self.spheresCheckbox.SetValue(self.networkHandler.unitcellAvailable)
            self.spheresCheckbox.Enable(self.networkHandler.unitcellAvailable)
            if not self.networkHandler.unitcellAvailable:
                self.spheresCheckbox.SetToolTip("No unitcell parsed into HDF5 file.")
            else:
                self.spheresCheckbox.SetToolTip("")

        elif self.networkHandler:
            # Disable charge visualization
            self.networkHandler.clear_processor_network()
            del self.networkHandler

    def reset_canvas_positions(self):
        window = self.GetTopLevelParent()
        print(window.GetPosition().x + window.GetSize().width)
        print(window.GetPosition().y)
        self.networkHandler.position_canvases(window.GetPosition().x + window.GetSize().width, window.GetPosition().y)



class BandSelectorWidget(wx.BoxSizer):
    # Class managing the UI for a single TF point in the collapsible
    def __init__(self, parent, band_choices):
        super().__init__(wx.HORIZONTAL)
        self.bandChooser = wx.Choice(parent, choices=band_choices)
        self.modeChooser = wx.Choice(parent, choices = ['Total', "Magnetic", "Up", "Down"])

        self.bandChooser.SetSelection(0)
        self.modeChooser.SetSelection(0)

        self.activeBand = None
        
        self.Add(self.bandChooser)
        self.Add(self.modeChooser)
    

        
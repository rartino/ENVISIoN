#
#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
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

import wx
from generalCollapsible import GeneralCollapsible
import parameter_utils
import inviwopy
# TODO: add option for transperacy before first tf point
# TODO maybe: add option for toggling tf points?

class VolumeControlCollapsible(GeneralCollapsible):
    def __init__(self, parent, label):
        super().__init__(parent, label = label)
        volumePane = self.GetPane()

        # Shading controls
        shadingHBox = wx.BoxSizer(wx.HORIZONTAL)
        shadingLabel = wx.StaticText(volumePane, label="Shading mode: ")
        shadingChoices = ["No Shading", "Ambient", "Diffuse", "Specular", "Blinn Phong", "Phong"]
        self.shadingDropDown = wx.Choice(volumePane,choices=shadingChoices)
        self.shadingDropDown.SetSelection(4)
        shadingHBox.Add(shadingLabel)
        shadingHBox.Add(self.shadingDropDown)
        self.add_item(shadingHBox)

        self.shadingDropDown.Bind(wx.EVT_CHOICE, self.shading_drop_down_changed)

        # Setup transfer function controls

        tfLabel = wx.StaticText(volumePane, label="Transfer Function: ")
        tfLabel.SetToolTip(
            "Edit the transfer function.\n" + 
            "Choose value from 0 to 1 in the first text field\n" +
            "Choose alpha from 0 to 1 in the second text field\n" + 
            "Choose color by clicking the color picker on the right\n" + 
            "Press \"+\" to add new point with specified values\n" + 
            "Press \"-\" to remove point")
        self.add_item(tfLabel)

        # Checkbox to choose transperancy before first tf point
        transperacyCheckbox = wx.CheckBox(volumePane, label="Transperancy before first point")
        transperacyCheckbox.SetToolTip(
            "If checked volume will be transperant at densities lower " +
            "than the first transfer function point.\n" + 
            "If unchecked lower densities will get an interpolated color.")
        transperacyCheckbox.Bind(wx.EVT_CHECKBOX, self.transperacy_checkbox_changed)

        transperacyCheckbox.SetValue(True)
        self.tf_transperancy_enabled = True

        self.add_item(transperacyCheckbox)

        # Vertical box to hold all tf point elements 
        self.tfpointsVBox = wx.BoxSizer(wx.VERTICAL)
        

        # List holds all added tfpoint sizers for later access
        # Empty on initialization, fills up with user input
        self.tfPointWidgets = []

        # Controls for adding new tf points
        self.tf_point_adder = TFPointWidget(volumePane, 0, 0, wx.Colour(0, 0, 0), button_label="+")
        self.tf_point_adder.button.Bind(wx.EVT_BUTTON, 
            lambda event : self.add_tf_point(
                self.tf_point_adder.valueText.GetLineText(0),
                self.tf_point_adder.alphaText.GetLineText(0),
                self.tf_point_adder.colorPicker.GetColour()))

        self.tfpointsVBox.Add(self.tf_point_adder)
        self.add_item(self.tfpointsVBox)

        #Histogram button
        histoButton = wx.Button(volumePane, label = "Show volume distribution", size = wx.Size(50, 23))
        histoButton.Bind(wx.EVT_BUTTON, lambda event : parameter_utils.show_volume_dist(self.parent_collapsible.parent_collapsible.path))

        # Load and save controls
        saveButton = wx.Button(volumePane, label = "Save transfer func", size = wx.Size(100, 23))
        loadButton = wx.Button(volumePane, label = "Load transfer func", size = wx.Size(100, 23))
        
        saveButton.Bind(wx.EVT_BUTTON, lambda event : self.save_transfer_function())
        loadButton.Bind(wx.EVT_BUTTON, lambda event : self.load_transfer_function())

        self.add_item(histoButton)
        self.add_item(saveButton)
        self.add_item(loadButton)
        
    def shading_drop_down_changed(self, event):
    # Change the shading mode
        self.networkHandler.set_shading_mode(self.shadingDropDown.GetCurrentSelection())

    def transperacy_checkbox_changed(self, event):
    # Update the transperancy mode
        self.tf_transperancy_enabled = event.IsChecked()
        self.update_mask()
        
    def update_mask(self):
    # Sets a mask to the transferfunction
    # Makes o
        if len(self.tfPointWidgets) <= 0:
            return
        if self.tf_transperancy_enabled:
            print("Add mask")
            self.networkHandler.set_mask(self.tfPointWidgets[0].value, 1)
        else:
            print("Reset mask")
            self.networkHandler.set_mask(0, 1)

    def load_transfer_function(self, path=None):
    # Save the transfer function to specified path
    # If no path is specified let the user pick one 
        if path == None:
            fileDialog = wx.FileDialog(self, "Load transfer function", wildcard="tf files (*.tf)|*.tf",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            fileDialog.ShowModal() 
            path = fileDialog.GetPath()
        # Open the file
        try:
            with open(path, 'r') as file:
                self.clear_tf_points()
                # Read each line and add a point for it
                for line in [x.strip() for x in file.readlines()]:
                    line = line.split()
                    self.add_tf_point(line[0], line[1], wx.Colour(int(line[2]), int(line[3]), int(line[4])))
        except:
            wx.LogError("Cannot open file '%s'." % path)

    def save_transfer_function(self, path=None):
    # Load transfer function from specified file
    # If no path is specified let the user pick one 
        if path == None:
        # Open a dialog to choose path
            fileDialog = wx.FileDialog(self, "Save transfer function", wildcard="tf files (*.tf)|*.tf",
                                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) 
            fileDialog.ShowModal() 
            path = fileDialog.GetPath()
            print(path)

        # Save the file
        try:
            with open(path, 'w') as file:
                for tfpt in self.tfPointWidgets:
                    # Write info for one point on each line
                    # Format: value alpha red green blue 
                    file.write(
                        str(tfpt.value) + " " + str(tfpt.alpha) + " " + 
                        str(tfpt.colour.Red()) + " "  + str(tfpt.colour.Green()) + " " + str(tfpt.colour.Blue()) + "\n")
                # for line in [x.strip() for x in file.readlines()]:
                #     line = line.split()
                #     file.
        except:
            wx.LogError("Cannot open file '%s'." % path)

    def add_tf_point(self, value, alpha, colour):
    # Adds a new tf point to volume rendering
    # Adds a ui element to show and edit the new point

        # Assert that user input is valid
        try:
            value = float(value)
            alpha = float(alpha)
        except:
            raise AssertionError("Input values must be valid float values")
        assert value >= 0 and 1 >= value, "Transfer function: Invalid value range"
        assert alpha >= 0 and 1 >= alpha, "Transfer function: Invalid alpha range"

        # Add point to GUI

        # Find the correct index to insert the new point at
        # Makes sure points are always sorted by value
        insertion_idx = len(self.tfPointWidgets)
        for i in range(len(self.tfPointWidgets)):
            item_value = self.tfPointWidgets[i].value
            if value == item_value:
                print("Cannot add tf point at exsisting value")
                return
            if value < item_value:
                insertion_idx = i
                break

        tfPointWidget = TFPointWidget(self.GetPane(), value, alpha, colour)

        self.tfpointsVBox.Insert(insertion_idx, tfPointWidget)

        # Set event bindings
        tfPointWidget.button.Bind(wx.EVT_BUTTON, lambda event : self.remove_tf_point(tfPointWidget))

        # Update on theese
        tfPointWidget.valueText.Bind(wx.EVT_KILL_FOCUS, lambda event : self.update_tf_point(tfPointWidget))
        tfPointWidget.valueText.Bind(wx.EVT_TEXT_ENTER, lambda event : self.update_tf_point(tfPointWidget))
        tfPointWidget.alphaText.Bind(wx.EVT_KILL_FOCUS, lambda event : self.update_tf_point(tfPointWidget))
        tfPointWidget.alphaText.Bind(wx.EVT_TEXT_ENTER, lambda event : self.update_tf_point(tfPointWidget))
        tfPointWidget.colorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, lambda event : self.update_tf_point(tfPointWidget))

        self.tfPointWidgets.insert(insertion_idx, tfPointWidget)
        self.update_collapse()
        
        # Update the transperancy mask
        self.update_mask()

        # Add point to inviwo
        glmColor = inviwopy.glm.vec4(float(colour.Red())/255, float(colour.Green())/255, float(colour.Blue())/255, alpha)
        self.networkHandler.add_tf_point(value, glmColor)

    def clear_tf_points(self):
        while len(self.tfPointWidgets) > 0:
            self.remove_tf_point(self.tfPointWidgets[0])

    def remove_tf_point(self, tfPointWidget):
    # Remove a tfPoint from inviwo processor and UI
        index = self.tfPointWidgets.index(tfPointWidget)

        # Removes the TFPointWidget and deletes all its child items
        tfPointWidget.Clear(delete_windows = True)
        self.tfPointWidgets.remove(tfPointWidget)
        self.tfpointsVBox.Remove(tfPointWidget)
        self.update_collapse()

        # Update the transperancy mask
        self.update_mask()

        # Remove point in inviwo
        self.networkHandler.remove_tf_point(index)

    def update_tf_point(self, tfPointWidget):
        # Update the tf point if its text or color is changed
        new_tf_data = tfPointWidget.read_inputs()
        self.remove_tf_point(tfPointWidget)
        self.add_tf_point(new_tf_data[0], new_tf_data[1], new_tf_data[2])


class TFPointWidget(wx.BoxSizer):
    # Class managing the UI for a single TF point in the collapsible
    def __init__(self, parent, value, alpha, colour, button_label="-"):
        super().__init__(wx.HORIZONTAL)

        self.value = float(value)
        self.alpha = float(alpha)
        self.colour = colour

        self.valueText = wx.TextCtrl(parent, value=str(value), style=wx.TE_PROCESS_ENTER, size=wx.Size(45, 23))
        self.alphaText = wx.TextCtrl(parent, value=str(alpha), style=wx.TE_PROCESS_ENTER, size=wx.Size(45, 23))
        self.button = wx.Button(parent, label = button_label, size = wx.Size(23, 23))

        self.colorPicker = wx.ColourPickerCtrl(parent, size=wx.Size(30, 23))
        self.colorPicker.SetColour(colour)

        self.Add(self.valueText)
        self.Add(self.alphaText)
        self.Add(self.colorPicker)
        self.Add(self.button)

    def get_text_value(self):
        try:
            return float(self.valueText.GetLineText(0))
        except:
            self.valueText.SetValue(str(self.value))
            raise AssertionError("Input values must be valid float values")

    def get_text_alpha(self):
        try:
            return float(self.alphaText.GetLineText(0))
        except:
            self.alphaText.SetValue(str(self.alpha))
            raise AssertionError("Input values must be valid float values")
    
    def read_inputs(self):
        # Read all input fields and resets variables
        res = [self.get_text_value(), self.get_text_alpha(), self.colorPicker.GetColour()]
        return res
        
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
# TODO: make Transferfunction saveable
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

        # ------------------------------------
        # --Setup transfer function controls--
        
        tfLabel = wx.StaticText(volumePane, label="Transfer Function: ")
        self.add_item(tfLabel)

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


    # Shader editing
    def shading_drop_down_changed(self, event):
        parameter_utils.charge_set_shading_mode(self.shadingDropDown.GetCurrentSelection())


    # Transfer function editing

    def add_tf_point(self, value, alpha, colour):
        # Adds a new tf point to volume rendering
        # Adds a ui element to show and edit the new point

        # TODO: Bind text field events to change the tf point
        # TODO: Sort by "value" so points are in correct order

        # Assert that user input is valid
        try:
            value = float(value)
            alpha = float(alpha)
        except:
            raise AssertionError("Input values must be valid float values")
        assert value >= 0 and 1 >= value, "Transfer function: Invalid value range"
        assert alpha >= 0 and 255 >= alpha, "Transfer function: Invalid alpha range"

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

        # Add point to inviwo
        glmColor = inviwopy.glm.vec4(float(colour.Red())/255, float(colour.Green())/255, float(colour.Blue())/255, alpha)
        parameter_utils.charge_add_tf_point(value, glmColor)

    def remove_tf_point(self, tfPointWidget):
        # Remove tfPoint from inviwo processor
        index = self.tfPointWidgets.index(tfPointWidget)
        parameter_utils.charge_remove_tf_point(index)

        # Removes the TFPointWidget and deletes all its child items
        tfPointWidget.Clear(delete_windows = True)
        self.tfPointWidgets.remove(tfPointWidget)
        self.tfpointsVBox.Remove(tfPointWidget)
        self.update_collapse()

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

        self.valueText = wx.TextCtrl(parent, value=str(value), style=wx.TE_PROCESS_ENTER)
        self.alphaText = wx.TextCtrl(parent, value=str(alpha), style=wx.TE_PROCESS_ENTER)
        self.button = wx.Button(parent, label = button_label, size = wx.Size(23, 23))

        self.colorPicker = wx.ColourPickerCtrl(parent)
        self.colorPicker.SetColour(colour)

        self.Add(self.valueText)
        self.Add(self.alphaText)
        self.Add(self.colorPicker)
        self.Add(self.button)

        # wx.EVT_SET_FOCUS EVT_KILL_FOCUS
        # self.valueText.Bind(wx.EVT_SET_FOCUS, lambda event: self.text_focused(
        #     self.valueText, 
        #     str(self.get_value()), 
        #     self.valueText.GetLineText(0)))


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


    # def text_focused(self, textCtrl, default_value, value):
    #     if default_value == value:
    #         textCtrl.SetValue("")

    #     print("text pressed")
    #     pass

    # def text_unfocused(self, event):
    #     pass
        
        
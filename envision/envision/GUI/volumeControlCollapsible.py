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
#  Alterations to this file by Anton Hjert
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


class VoluneControlCollapsible(GeneralCollapsible):
    def __init__(self, parent, label):
        super().__init__(parent, label = label)

        volumePane = self.GetPane()

        # Shading controls
        shadingHBox = wx.BoxSizer(wx.HORIZONTAL)
        shadingLabel = wx.StaticText(volumePane, label="Shading mode: ")
        shadingDropDown = wx.ComboBox(volumePane,
                                    value = "Default",
                                    choices= ("mode2","mode3","mode4"))
        shadingHBox.Add(shadingLabel)
        shadingHBox.Add(shadingDropDown)
        self.add_item(shadingHBox)

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
        # self.tf_point_adder = TFPointWidget(volumePane, 0, 0, wx.Colour(0, 0, 0), button_label="+")
        self.tf_point_adder.button.Bind(wx.EVT_BUTTON, 
            lambda event : self.add_tf_point(
                self.tf_point_adder.valueText.GetLineText(0),
                self.tf_point_adder.alphaText.GetLineText(0),
                self.tf_point_adder.colorPicker.GetColour()))
        self.tfpointsVBox.Add(self.tf_point_adder)

        self.add_item(self.tfpointsVBox)

    def add_tf_point(self, value, alpha, colour):
        # Adds a new tf point to volume rendering
        # Adds a ui element to show and edit the new point

        # TODO: Bind text field events to change the tf point
        # TODO: Sort by "value" so points are in correct order
        try:
            value = float(value)
            alpha = float(alpha)
        except:
            raise AssertionError("Input values must be valid float values")
        
        assert value >= 0 and 1 >= value, "Transfer function: Invalid value range"
        assert alpha >= 0 and 255 >= alpha, "Transfer function: Invalid alpha range"

        # Find the correct index to insert the new point at
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

        tfPointWidget.button.Bind(wx.EVT_BUTTON, lambda event : self.remove_tf_point(tfPointWidget))

        self.tfPointWidgets.insert(insertion_idx, tfPointWidget)
        self.update_collapse()

    def remove_tf_point(self, tfPointWidget):
        # Removes tfPoint from inviwo processor
        # Removes the TFPointWidget and deletes all its child items

        # TODO remove tf point in inviwo

        tfPointWidget.Clear(delete_windows = True)
        self.tfPointWidgets.remove(tfPointWidget)
        self.tfpointsVBox.Remove(tfPointWidget)
        self.update_collapse()



class TFPointWidget(wx.BoxSizer):
    # Class managing the UI for a single TF point in the collapsible
    def __init__(self, parent, value, alpha, colour, button_label="-"):
        super().__init__(wx.HORIZONTAL)

        self.value = float(value)
        self.alpha = float(alpha)
        self.colour = colour

        self.valueText = wx.TextCtrl(parent, value=str(value))
        self.alphaText = wx.TextCtrl(parent, value=str(alpha))
        self.button = wx.Button(parent, label = button_label, size = wx.Size(23, 23))

        self.colorPicker = wx.ColourPickerCtrl(parent)
        self.colorPicker.SetColour(colour)

        self.Add(self.valueText)
        self.Add(self.alphaText)
        self.Add(self.colorPicker)
        self.Add(self.button)
        
        
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
from generalCollapsible import GeneralCollapsible
from parameter_utils import charge_set_background
import inviwopy
# TODO: make Transferfunction saveable
# TODO: add option for transperacy before first tf point
# TODO maybe: add option for toggling tf points?

class BackgroundCollapsible(GeneralCollapsible):
    def __init__(self, parent, label):
        super().__init__(parent, label = label)
        backgroundPane = self.GetPane()

        # style controls
        backgroundSizer = wx.BoxSizer(wx.HORIZONTAL)
        backgroundLabel = wx.StaticText(backgroundPane, label="Background style: ")
        backgroundChoices = ["Linear gradient (Vertical)", "Linear gradient (Horizontal)", 
                            "Linear gradient (Spherical)", "Uniform Color", "Checker board"]
        self.backgroundDropDown = wx.Choice(backgroundPane,choices=backgroundChoices)
        self.backgroundDropDown.SetSelection(0)
        backgroundSizer.Add(backgroundLabel)
        backgroundSizer.Add(self.backgroundDropDown)
        self.add_item(backgroundSizer)

        self.backgroundDropDown.Bind(wx.EVT_CHOICE, self.background_drop_down_changed)

        # ------------------------------------
        # --Setup background controls--
        
        bgColourLabel = wx.StaticText(backgroundPane, label="Background colors:")
        self.add_item(bgColourLabel)

        # Vertical box to hold all background colour elements 
        self.bgColourSizer = wx.BoxSizer(wx.VERTICAL)
        
        # List holds all added background sizers for later access
        self.bgColourPicker1 = self.add_bg_widget(0.000,0.000,0.000,1.000,wx.Colour(0, 0, 0))
        self.bgColourPicker2 = self.add_bg_widget(1.000,1.000,1.000,1.000,wx.Colour(255, 255, 255))
        self.bgColourSizer.Add(self.bgColourPicker1)
        self.bgColourSizer.Add(self.bgColourPicker2)
        self.add_item(self.bgColourSizer)

    #Button for switching the two colours with each other
        switchButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.switchColourButton = wx.Button(backgroundPane, label = "Switch colors")
        switchButtonSizer.Add(self.switchColourButton)
        self.add_item(switchButtonSizer)
        self.switchColourButton.Bind(wx.EVT_BUTTON, self.colour_switch)

    # blend controls
        blendSizer = wx.BoxSizer(wx.HORIZONTAL)
        blendLabel = wx.StaticText(backgroundPane, label="Blend mode: ")
        blendChoices = ["Back To Front (Pre-multiplied)", "Alpha Mixing"]
        self.blendDropDown = wx.Choice(backgroundPane,choices=blendChoices)
        self.blendDropDown.SetSelection(0)
        blendSizer.Add(blendLabel)
        blendSizer.Add(self.blendDropDown)
        self.add_item(blendSizer)

        self.blendDropDown.Bind(wx.EVT_CHOICE, self.blend_drop_down_changed)

    def colour_switch(self,event):
        colour1 = self.bgColourPicker1.read_inputs()
        colour2 = self.bgColourPicker2.read_inputs()
        self.bgColourPicker1.write_inputs(colour2[0], colour2[1], colour2[2],
                                        colour2[3], colour2[4])
        self.bgColourPicker2.write_inputs(colour1[0], colour1[1], colour1[2],
                                        colour1[3], colour1[4])
        self.update_bg_colour()

    # background and blend editing
    def background_drop_down_changed(self, event):
        self.update_bg_colour()

    def blend_drop_down_changed(self,event):
        self.update_bg_colour()

    # Transfer function editing

    def add_bg_widget(self, value1, value2, value3, value4, colour):
        # Adds a new background colour picker
        # Assert that user input is valid
        try:
            value1 = float(value1)
            value2 = float(value2)
            value3 = float(value3)
            value4 = float(value4)
        except:
            raise AssertionError("Input values must be valid float values")
        assert value1 >= 0 and 1 >= value1, "Invalid value range"
        assert value2 >= 0 and 1 >= value2, "Invalid value range"
        assert value3 >= 0 and 1 >= value3, "Invalid value range"
        assert value4 >= 0 and 1 >= value4, "Invalid value range"

        bgColourWidget = BgColourWidget(self.GetPane(), value1, value2, value3, value4, colour)

        # Set event bindings

        # Update on theese
        bgColourWidget.value1Text.Bind(wx.EVT_KILL_FOCUS, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value1Text.Bind(wx.EVT_TEXT_ENTER, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value2Text.Bind(wx.EVT_KILL_FOCUS, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value2Text.Bind(wx.EVT_TEXT_ENTER, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value3Text.Bind(wx.EVT_KILL_FOCUS, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value3Text.Bind(wx.EVT_TEXT_ENTER, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value4Text.Bind(wx.EVT_KILL_FOCUS, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.value4Text.Bind(wx.EVT_TEXT_ENTER, lambda event : self.new_text_colour(bgColourWidget))
        bgColourWidget.colorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, lambda event : self.new_colourpicker_colour(bgColourWidget))

        self.update_collapse()
        return bgColourWidget


    def update_bg_colour(self, event = None):
        # Update the tf point if its text or color is changed
        new_bg_colour1 = self.bgColourPicker1.read_inputs()
        bgc1 = inviwopy.glm.vec4(new_bg_colour1[0],new_bg_colour1[1],new_bg_colour1[2],new_bg_colour1[3])
        new_bg_colour2 = self.bgColourPicker2.read_inputs()
        bgc2 = inviwopy.glm.vec4(new_bg_colour2[0],new_bg_colour2[1],new_bg_colour2[2],new_bg_colour2[3])
        charge_set_background(bgc1,bgc2,
                            self.backgroundDropDown.GetCurrentSelection(),
                            self.blendDropDown.GetCurrentSelection())

    def new_text_colour(self,bgWidget):
        colour = bgWidget.read_inputs()
        colourItem = wx.Colour(colour[0]*255, colour[1]*255, colour[2]*255, colour[3]*255)
        bgWidget.colorPicker.SetColour(colourItem)
        self.update_bg_colour()

    def new_colourpicker_colour(self,bgWidget):
        colour = bgWidget.colorPicker.GetColour()
        colourList = [float(colour.Red())/255, float(colour.Green())/255, float(colour.Blue())/255, float(colour.Alpha())/255]
        bgWidget.write_inputs(colourList[0],colourList[1],colourList[2],1.000,colour)
        self.update_bg_colour()



class BgColourWidget(wx.BoxSizer):
    # Class managing the UI for a single TF point in the collapsible
    def __init__(self, parent, value1, value2, value3, value4, colour):
        super().__init__(wx.HORIZONTAL)

        self.value1 = float(value1)
        self.value2 = float(value2)
        self.value3 = float(value3)
        self.value4 = float(value4)
        self.colour = colour

        self.value1Text = wx.TextCtrl(parent, size=wx.Size(50,30), value=str(value1), style=wx.TE_PROCESS_ENTER)
        self.value2Text = wx.TextCtrl(parent, size=wx.Size(50,30), value=str(value2), style=wx.TE_PROCESS_ENTER)
        self.value3Text = wx.TextCtrl(parent, size=wx.Size(50,30), value=str(value3), style=wx.TE_PROCESS_ENTER)
        self.value4Text = wx.TextCtrl(parent, size=wx.Size(50,30), value=str(value4), style=wx.TE_PROCESS_ENTER)

        self.colorPicker = wx.ColourPickerCtrl(parent)
        self.colorPicker.SetColour(colour)

        self.Add(self.colorPicker)
        self.Add(self.value1Text)
        self.Add(self.value2Text)
        self.Add(self.value3Text)
        self.Add(self.value4Text)

        # wx.EVT_SET_FOCUS EVT_KILL_FOCUS
        # self.valueText.Bind(wx.EVT_SET_FOCUS, lambda event: self.text_focused(
        #     self.valueText, 
        #     str(self.get_value()), 
        #     self.valueText.GetLineText(0)))


    def get_text_value1(self):
        try:
            return float(self.value1Text.GetLineText(0))
        except:
            self.value1Text.SetValue(str(self.value1))
            raise AssertionError("Input values must be valid float values")

    def get_text_value2(self):
        try:
            return float(self.value2Text.GetLineText(0))
        except:
            self.value2Text.SetValue(str(self.value2))
            raise AssertionError("Input values must be valid float values")

    def get_text_value3(self):
            try:
                return float(self.value3Text.GetLineText(0))
            except:
                self.value3Text.SetValue(str(self.value3))
                raise AssertionError("Input values must be valid float values")

    def get_text_value4(self):
        try:
            return float(self.value4Text.GetLineText(0))
        except:
            self.value4Text.SetValue(str(self.value4))
            raise AssertionError("Input values must be valid float values")
    
    def read_inputs(self):
        # Read all input fields and resets variables
        
        res = [self.get_text_value1(), self.get_text_value2(), self.get_text_value3(), 
                self.get_text_value4(), self.colorPicker.GetColour()]
        return res

    def write_inputs(self, value1, value2, value3, value4, colour):
        self.value1 = value1
        self.value1Text.SetValue("{0:.3f}".format(value1))
        self.value2 = value2
        self.value2Text.SetValue("{0:.3f}".format(value2))
        self.value3 = value3
        self.value3Text.SetValue("{0:.3f}".format(value3))
        self.value4 = value4
        self.value4Text.SetValue("{0:.3f}".format(value4))
        self.colour = colour
        self.colorPicker.SetColour(colour)

    # def text_focused(self, textCtrl, default_value, value):
    #     if default_value == value:
    #         textCtrl.SetValue("")

    #     print("text pressed")
    #     pass

    # def text_unfocused(self, event):
    #     pass
        
    
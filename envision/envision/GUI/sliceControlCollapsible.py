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
from backgroundCollapsible import BackgroundCollapsible
# TODO: Integrate with inviwo
# TODO: height slider does not work with custom normal

class SliceControlCollapsible(GeneralCollapsible):
    def __init__(self, parent, label):
        super().__init__(parent, label = label)
        
        pane = self.GetPane()

        # Plane normal controls
        normalLabel = wx.StaticText(pane, label="Slice plane normal:")
        normalLabel.SetToolTip(
            "Set the normal vector of slice plane\n" + 
            "Input X, Y, and Z component in text fields.")
        self.add_item(normalLabel)

        self.xInput = wx.TextCtrl(pane, value="0", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))
        self.yInput = wx.TextCtrl(pane, value="1", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))
        self.zInput = wx.TextCtrl(pane, value="0", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))

        #Setup the possibility of slice-background control
        self.sliceBackgroundCollapsibe = BackgroundCollapsible(self.GetPane(), "Slice background")
        self.sliceBackgroundCollapsibe.type = 'SliceBackground'
        self.sliceBackgroundCollapsibe.SetLabel('Slice Background')
        self.sliceBackgroundCollapsibe.backgroundDropDown.SetSelection(3)
        self.sliceBackgroundCollapsibe.bgColourPicker1.write_inputs(0, 0, 0, 1,wx.Colour(0,0,0))
        self.sliceBackgroundCollapsibe.bgColourPicker2.write_inputs(1, 1, 1, 1,wx.Colour(255,255,255))

        normalHBox = wx.BoxSizer(wx.HORIZONTAL)
        normalHBox.Add(self.xInput)
        normalHBox.Add(self.yInput)
        normalHBox.Add(self.zInput)
        self.add_item(normalHBox)
        
        # Events to read input on
        self.xInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.xInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)
        self.yInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.yInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)
        self.zInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.zInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)

        sliderLabel = wx.StaticText(pane, label="Slice plane height:")
        sliderLabel.SetToolTip(
            "Use the slider to select height of slice plane\n" + 
            "0% - Bottom of the volume\n" + 
            "100% - Top of the volume")
        self.add_item(sliderLabel)

        # Plane mover slider
        self.heightSlider = wx.Slider(pane, minValue=0, maxValue=100, value=50)
        self.heightSlider.Bind(wx.EVT_SCROLL, self.slider_changed)

        self.add_item(self.heightSlider)
        self.add_sub_collapsible(self.sliceBackgroundCollapsibe)

    def normal_input_changed(self, event):
        # TODO clamp values in [0, 1] range
        try:
            x = float(self.xInput.GetLineText(0))
            y = float(self.yInput.GetLineText(0))
            z = float(self.zInput.GetLineText(0))
        except:
            raise ValueError("Input values must be valid float values")

        if x == y == z == 0:
            raise ValueError("Normal must be separated from 0")

        parameter_utils.charge_set_plane_normal(x, y, z)
        print(str(x) + ":" + str(y) + ":" + str(z))

    def slider_changed(self, event):
        height = float(self.heightSlider.GetValue()) / 100
        parameter_utils.charge_set_plane_height(height)





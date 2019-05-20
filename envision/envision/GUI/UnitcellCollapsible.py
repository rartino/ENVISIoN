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
import inviwopy
import math

class UnitcellCollapsible(GeneralCollapsible):
# Collapsible panel for handling unitcell part of visualization
    def __init__(self, parent):
        super().__init__(parent, label = "Atom rendering")
        self.noDataText = wx.StaticText(self.GetPane(),
                                    label="No unitcell data in hdf5 file.\n"+
                                          "IF you expect there to be unitcell data,\n"+
                                          "make sure you parsed it to the hdf5 file.")
        self.add_item(self.noDataText)

        self.hasAtoms = False
        self.unitcellWidgets = []

    def add_atom_control(self, atomName, atomIndex):
    # Add unitcell control widget with name and index
    # Clears old widgets if self.hasAtoms is false
        if not self.hasAtoms:
            if self.noDataText:
                self.noDataText.Destroy()
            for widget in self.unitcellWidgets:
                self.sizer.Remove(widget)
            self.unitcellWidgets.clear()
            self.hasAtoms = True
        print("Adding: " + str(atomName) + ", " + str(atomIndex))
        unitcellWidget = UnitcellControlWidget(self.GetPane(), atomName, atomIndex, self.networkHandler)
        self.unitcellWidgets.append(unitcellWidget)
        self.add_item(unitcellWidget)

class UnitcellControlWidget(wx.BoxSizer):
    # Widget for controling unitcell properties of a single atom type.

    def __init__(self, parent, atomName, atomIndex, networkHandler):
        super().__init__(wx.VERTICAL)

        self.index = atomIndex
        self.atomName = atomName
        self.networkHandler = networkHandler

        nameText = wx.StaticText(parent, label=atomName + " radius:")
        radiusSlider = wx.Slider(parent, minValue=0, maxValue=100, value=3)

        self.Add(nameText)
        self.Add(radiusSlider)

        radiusSlider.Bind(wx.EVT_SCROLL, self.slider_changed)
    
    def slider_changed(self, event):
        val = math.pow(1.0243, float(event.GetPosition())) - 1
        self.networkHandler.set_atom_radius(val, self.index) 


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
import parameter_utils
from generalCollapsible import GeneralCollapsible

class ParchgFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Partial Charge")
        
        # Setup band chooser choise box

        # List containing the band selector widgets
        self.selectorWidgets = []

        # List of possible band choices, fills up based on selected hdf5 file
        self.bandChoices = ['None', '1']
        
        # Initialize the first band selector widget
        bandSelector = BandSelectorWidget(self.GetPane(), self.bandChoices)
        self.selectorWidgets.append(bandSelector)
        
        bandSelector.bandChooser.Bind(wx.EVT_CHOICE, lambda event : self.band_selection_changed(bandSelector))
        bandSelector.modeChooser.Bind(wx.EVT_CHOICE, lambda event : self.mode_selection_changed(bandSelector))

        button = wx.Button(self.GetPane(), label = "Press me", size = wx.Size(100, 23))
        button2 = wx.Button(self.GetPane(), label = "Press me", size = wx.Size(100, 23))


        # Add stuff to sizer
        self.selectorVBox = wx.BoxSizer(wx.VERTICAL)
        self.selectorVBox.Add(bandSelector)

        self.add_item(self.selectorVBox)
        self.add_item(button)
        self.add_item(button2)

        # Bind events
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)
        button.Bind(wx.EVT_BUTTON, self.on_press)
        button2.Bind(wx.EVT_BUTTON, self.on_press2)

    def on_press(self, event):
        self.networkHandler.clear_band_processors()
    
    def on_press2(self, event):
        self.networkHandler.select_bands([0, 0], [0, 1])

    def band_selection_changed(self, selectorWidget):

        # If its the bottom one dont remove it and add new ones if set to a value.
        print(selectorWidget)

        # TODO only add new one if changed from 'None'
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
            newBandSelector.modeChooser.Bind(wx.EVT_CHOICE, lambda event : self.mode_selection_changed(newBandSelector))
            #self.selectorVBox.Insert(len(self.selectorWidgets)-1, newBandSelector)
            self.selectorVBox.Add(newBandSelector)
            self.selectorWidgets.append(newBandSelector)

        elif selectedString != 'None':
        # Selection was changed from one number to another.
            pass

        self.reload_band_processors()
        self.update_collapse()
    

        self.update_collapse()

    def reload_band_processors(self):
        bandList = []
        modeList = []
        for widget in self.selectorWidgets:
            try:
                bandList.append(int(widget.bandChooser.GetString(widget.bandChooser.GetSelection())))
                modeList.append(widget.modeChooser.GetSelection())
            except ValueError:
                continue
        self.networkHandler.select_bands(bandList, modeList)
            

    def mode_selection_changed(self, event):
        pass



    def on_collapse(self, event = None):
        self.update_collapse()

        if self.IsCollapsed():
            del self.networkHandler
            parameter_utils.clear_processor_network()
        else:
            # bandKeys = parameter_utils.parchg_get_bands(self.parent_collapsible.path)
            # for key in bandKeys:
            #     self.bandChoices.append(key)
            # for b in self.selectorWidgets:
            #     b.bandChooser.Clear()
            #     b.bandChooser.AppendItems(self.bandChoices)
            #     b.bandChooser.SetSelection(0)
            self.networkHandler = parameter_utils.start_parchg_vis(self.parent_collapsible.path)


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
    

        
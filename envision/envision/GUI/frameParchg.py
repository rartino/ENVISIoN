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
        self.bandChoosers = []
        self.modeChoosers = []
        choiceSizer = wx.GridSizer(2, wx.Size(2, 2))

        # TODO add labels

        for i in range(4):
            bandChooser = wx.Choice(self.GetPane(), choices = ['None'])
            modeChooser = wx.Choice(self.GetPane(), choices = ['Total', "Something"])
            bandChooser.SetSelection(0)
            modeChooser.SetSelection(1)
            choiceSizer.Add(bandChooser)
            choiceSizer.Add(modeChooser)
            self.bandChoosers.append(bandChooser)
            self.modeChoosers.append(modeChooser)


        # Add stuff to sizer
        self.add_item(choiceSizer)


        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    
    def on_collapse(self, event = None):
        self.update_collapse()

        if self.IsCollapsed():
            parameter_utils.clear_processor_network()
        else:
            bandKeys = parameter_utils.parchg_get_bands(self.parent_collapsible.path)
            for key in bandKeys:
                self.bandChoosers[0].Append(key)
                self.bandChoosers[1].Append(key)
                self.bandChoosers[2].Append(key)
                self.bandChoosers[3].Append(key)
            parameter_utils.start_parchg_vis(self.parent_collapsible.path)


    def start_vis(self):
        if self.isPathEmpty():
            return
        
        # try:
        self.start_vis()
        # except:
            # print("Wawa")

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

"""*****************************************************************************"""
"""This file sets up the visualization-section of the GUI, a collapsible pane.  """
"""The subsections of this pane is either items, such as boxes, or collapsible  """
"""panes.                                                                       """
"""*****************************************************************************"""
import wx, sys, os

from frameCharge import ChargeFrame
from framePKF import PKFFrame
from frameDoS import DosFrame
from frameParchg import ParchgFrame

from generalCollapsible import GeneralCollapsible

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision"))
import envision
import envision.inviwo
import parameter_utils


class VisualizationFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Visualization")

    #Path-selection to file for visualization
        self.fileText = wx.StaticText(self.GetPane(), label="File to Visualize:")
        
        self.fileText.SetForegroundColour(self.text_colour)                                    
        self.path = "Enter path.."
        self.chooseFile = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterPath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value=self.path,
                                    style=wx.TE_PROCESS_ENTER)
        
        self.add_item(self.fileText)
        self.add_item(self.enterPath)
        self.add_item(self.chooseFile)

    # Initializa all the collapsible visualization menues
        chargeFrame = ChargeFrame(self.GetPane())
        pcFrame = PKFFrame(self.GetPane())
        dosFrame = DosFrame(self.GetPane())
        parchgFrame = ParchgFrame(self.GetPane())

    # Add them to the sizer
        self.add_sub_collapsible(chargeFrame)
        self.add_sub_collapsible(pcFrame)
        self.add_sub_collapsible(dosFrame)
        self.add_sub_collapsible(parchgFrame)

    # Set some callbacks
        self.chooseFile.Bind(wx.EVT_BUTTON, self.file_pressed)
        self.enterPath.Bind(wx.EVT_TEXT_ENTER, self.path_OnEnter)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_change)


    def on_change(self, event):
        if self.IsCollapsed():
            print("Collapsed Visualization")
        else:
            print("Extended Visualization")
        self.update_collapse()

    def file_pressed(self,event):
        fileFrame = wx.Frame(None, -1, 'win.py',size=wx.Size(200,50))
        openFileDialog = wx.FileDialog(fileFrame, "Open", "", "", 
                                      "HDF5 files (*.hdf5)|*.hdf5", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.path = openFileDialog.GetPath()
        openFileDialog.Destroy()
        fileFrame.Destroy()
        self.enterPath.SetValue(self.path)
        print(self.path)

    #When path entered in text and Enter-key is pressed
    def path_OnEnter(self,event):
        tmpPath = self.enterPath.GetLineText(0)
        if not os.path.exists(tmpPath):
            messageFrame = wx.Frame(None, -1, 'win.py',size=wx.Size(60,50))
            openPathDialog = wx.MessageDialog(messageFrame,  
                                        tmpPath+
                                        " not a valid directory!",
                                        "Failed!", 
                                        wx.FD_OPEN)
            openPathDialog.ShowModal()
            openPathDialog.Destroy()
            messageFrame.Destroy()
        else: 
            self.path = tmpPath

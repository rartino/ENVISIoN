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

sys.path.insert(0, os.path.expanduser(os.getcwd()))
from frameCharge import ChargeFrame
from framePKF import PKFFrame
from frameDoS import DosFrame
from frameParchg import ParchgFrame
from frameUnitcell import UnitcellFrame

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision"))
import envision
import envision.inviwo
import parameter_utils
PATH_TO_HDF5=os.path.expanduser("C:/Users/sille/Downloads/demo_charge.hdf5")

class VisualizationFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        #Setup style of the panes
        visSizer = wx.BoxSizer(wx.VERTICAL)
        visPane = self.GetPane()
        self.bg_colour = wx.Colour(76,75,77)
        self.text_colour = wx.Colour(255,255,255)
        self.SetBackgroundColour(self.bg_colour)
        self.itemSize = wx.Size(150,25)
        
        #Path-selection to file for visualization
        self.fileText = wx.StaticText(self.GetPane(),
                                    label="File to Visualize:")
        self.fileText.SetForegroundColour(self.text_colour)                                    
        self.path = "Enter path.."
        self.chooseFile = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterPath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value=self.path,
                                    style=wx.TE_PROCESS_ENTER)
        visSizer.Add(self.fileText, wx.GROW,0)
        visSizer.Add(self.enterPath, wx.GROW,0)
        visSizer.Add(self.chooseFile,wx.GROW,0)

        #init and add all pane-elements in visFrame
        self.PKFFrame = PKFFrame(visPane,label="PKF")
        self.chargeFrame = ChargeFrame(visPane,label="Charge")
        self.dosFrame = DosFrame(visPane,label="Density Of State")
        self.parchgFrame = ParchgFrame(visPane,label="Charge")
        self.unitcellFrame = UnitcellFrame(visPane,label="Unitcell")
        visSizer.Add(self.chargeFrame,0)
        visSizer.Add(self.PKFFrame,0)
        visSizer.Add(self.dosFrame,0)
        visSizer.Add(self.parchgFrame,0)
        visSizer.Add(self.unitcellFrame,0)
        
        #Setup style of the sub-panes
        self.PKFFrame.SetBackgroundColour(self.bg_colour)
        self.chargeFrame.SetBackgroundColour(self.bg_colour)
        self.dosFrame.SetBackgroundColour(self.bg_colour)
        self.parchgFrame.SetBackgroundColour(self.bg_colour)
        self.unitcellFrame.SetBackgroundColour(self.bg_colour)

        #Help-variable to check if each section is closed.
        self.dosCollapsed = True
        self.parchgCollapsed = True
        self.unitcellCollapsed = True
        self.chargeCollapsed = True
        self.PKFCollapsed = True
        self.collapsed = True

        self.chooseFile.Bind(wx.EVT_BUTTON,self.file_pressed)
        self.enterPath.Bind(wx.EVT_TEXT_ENTER,self.path_OnEnter)
    
        visPane.SetSizer(visSizer)


    def on_change(self, event):
        self.GetParent().Layout()
        if self.collapsed:
            #when Vis-frame is collapsed, collapse all subframes
            self.collapse_all()
        elif not self.collapsed:
            self.collapsed = True
            print('HEJ')

    def PKF_change(self, event):
        if not self.collapsed:
            self.update_self()
        if self.PKFCollapsed:
            #PKF-function
            print('PKF')
            self.PKFCollapsed = False
        else:
            print('notPKF')
            self.PKFCollapsed = True

    def charge_change(self, event):
        if not self.collapsed:
            self.update_self()
        if self.chargeCollapsed:
            self.chargeCollapsed = False
            envision.inviwo.charge(self.path, iso = None,
                               slice = False, xpos = 0, ypos = 0)
            print('Charge')
        else:
            print('notCharge')
            self.chargeCollapsed = True

    def dos_change(self, event):
        if not self.collapsed:
            self.update_self()
        if self.dosCollapsed:
            #DoS-function
            print('DoS')
            self.dosCollapsed = False
        else:
            print('notDoS')
            self.dosCollapsed = True

    def parchg_change(self, event):
        if not self.collapsed:
            self.update_self()
        if self.parchgCollapsed:
            #parchg-function
            print('parchg')
            self.parchgCollapsed = False
        else:
            print('notparchg')
            self.parchgCollapsed = True

    def unitcell_change(self, event):
        if not self.collapsed:
            self.update_self()
        if self.unitcellCollapsed:
            #unitcell-function
            print('unitcell')
            self.unitcellCollapsed = False
        else:
            print('notunitcell')
            self.unitcellCollapsed = True

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
    
    def update_self(self):
        self.Collapse(True)
        self.Collapse(False)

    def collapse_all(self):
        self.chargeFrame.Collapse(True)
        self.PKFFrame.Collapse(True)
        self.dosFrame.Collapse(True)
        self.parchgFrame.Collapse(True)
        self.unitcellFrame.Collapse(True)
        self.collapsed = False
        self.chargeCollapsed = True
        self.PKFCollapsed = True
        self.dosCollapsed = False
        self.parchgCollapsed = True
        self.unitcellCollapsed = True
        
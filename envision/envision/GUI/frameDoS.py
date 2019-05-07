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
import wx ,sys ,os , h5py
import parameter_utils
from generalCollapsible import GeneralCollapsible
import envision

class DosFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Density of States")
    
        button1 = wx.Button(self.GetPane(), label="X")
        button2 = wx.Button(self.GetPane(), label="Y")
        slider = wx.Slider(self.GetPane())
        self.window1 = wx.CheckBox(self.GetPane(), label="Enable window 1")
        self.window2 = wx.CheckBox(self.GetPane(), label="Enable window 2")
        self.window3 = wx.CheckBox(self.GetPane(), label="Enable window 3")
        self.window4 = wx.CheckBox(self.GetPane(), label="Enable window 4")

        self.add_item(button1)
        self.add_item(button2)
        self.add_item(slider)
        self.add_item(self.window1)
        self.add_item(self.window2)
        self.add_item(self.window3)
        self.add_item(self.window4)

        self.window1.Bind(wx.EVT_CHECKBOX, self.on_check1)
        self.window2.Bind(wx.EVT_CHECKBOX, self.on_check2)
        self.window3.Bind(wx.EVT_CHECKBOX, self.on_check3)
        self.window4.Bind(wx.EVT_CHECKBOX, self.on_check4)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    
    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable DoS vis
            parameter_utils.clear_processor_network()
            self.window1.SetValue(False)
            self.window2.SetValue(False)
            self.window3.SetValue(False)
            self.window4.SetValue(False)
        else:
            self.start_vis()

    def start_vis(self):
        if self.isPathEmpty():
            return    
        elif '/FermiEnergy' in  h5py.File(self.parent_collapsible.path, 'r')\
            and 'DOS' in  h5py.File(self.parent_collapsible.path, 'r'):
            #Start DoS vis
            self.open_message("When hitting ok, wait until all four windows are fully loaded",
                            "Be patient!")
            envision.inviwo.dos(self.parent_collapsible.path, 
                                atom = 0, xpos = 0, ypos = 0)
            self.set_canvas_pos('DoS')
            self.window1.SetValue(True)
            self.window2.SetValue(True)
            self.window3.SetValue(True)
            self.window4.SetValue(True)
        else:
            self.open_message('The file of choice does not contain DoS-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()

    def on_check1(self,event):
        if self.window1.IsChecked():
            self.enable_window(True,'DOS Canvas')
            print('oncheck1')
        else:
            self.enable_window(False,'DOS Canvas')

    def on_check2(self,event):
        if self.window2.IsChecked():
            self.enable_window(True,'DOS Canvas2')
        else:
            self.enable_window(False,'DOS Canvas2')

    def on_check3(self,event):
        if self.window3.IsChecked():
            self.enable_window(True,'DOS Canvas3')
        else:
            self.enable_window(False,'DOS Canvas3')

    def on_check4(self,event):
        if self.window4.IsChecked():
            self.enable_window(True,'DOS Canvas4')
        else:
            self.enable_window(False,'DOS Canvas4')

    def enable_window(self,show,type):
        parameter_utils.show_canvas(show,type)
        print('enable')

    
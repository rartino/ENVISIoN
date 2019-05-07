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

class BandstructureFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Bandstructure")

        #Sizer for scale
        self.scaleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.scaleText = wx.StaticText(self.GetPane(),label="Scale: ")
        self.scale = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Scale')
        self.scaleBox.Add(self.scaleText)
        self.scaleBox.Add(self.scale)

        #Sizer for X range
        self.xRangeBox = wx.BoxSizer(wx.HORIZONTAL)
        self.xRangeText = wx.StaticText(self.GetPane(),label="X Range: ")
        self.xRangeMax = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Max')
        self.xRangeMin = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Min')
        self.xRangeBox.Add(self.xRangeText)
        self.xRangeBox.Add(self.xRangeMin)
        self.xRangeBox.Add(self.xRangeMax)
        
        #Sizer for Y range
        self.yRangeBox = wx.BoxSizer(wx.HORIZONTAL)
        self.yRangeText = wx.StaticText(self.GetPane(),label="Y Range: ")
        self.yRangeMax = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Max')
        self.yRangeMin = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Min')
        self.yRangeBox.Add(self.yRangeText)
        self.yRangeBox.Add(self.yRangeMin)
        self.yRangeBox.Add(self.yRangeMax)
        
        #Help line
        self.selectLine = wx.CheckBox(self.GetPane(),label='Help line: ')
        self.lineSlider = wx.Slider(self.GetPane())

        #Add items
        self.add_item(self.xRangeBox)
        self.add_item(self.yRangeBox)
        self.add_item(self.scaleBox)
        self.add_item(self.selectLine)
        self.add_item(self.lineSlider)
        

        self.scale.Bind(wx.EVT_TEXT_ENTER, self.on_scale_change)
        self.xRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_xmax_change)
        self.xRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_xmin_change)
        self.yRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_ymax_change)
        self.yRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_ymin_change)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)    
        self.selectLine.Bind(wx.EVT_CHECKBOX, self.on_check_line)
        self.lineSlider.Bind(wx.EVT_SLIDER, self.on_slide_line)
        #self.selectX.Bind(wx.EVT_CHOICE, self.on_changed_x)
    
    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable Bandstrucutre vis
            parameter_utils.clear_processor_network()
            self.selectAll.SetValue(False)
        else:
            self.start_vis()

    def start_vis(self):
        if self.isPathEmpty():
            return    
        elif '/Bandstructure' in  h5py.File(self.parent_collapsible.path, 'r'):
            #Start Bandstructure vis
            envision.inviwo.bandstructure(self.parent_collapsible.path, 
                                        xpos = 0, ypos = 0)
            parameter_utils.set_all_data('Line plot',True)
            self.scale.SetValue(str(parameter_utils.get_scale()))
            self.init_ranges()
            self.lineSlider.SetMax(parameter_utils.get_x_range()[0])
            self.set_canvas_pos()
        else:
            self.open_message('The file of choice does not contain Bandstructure-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()

    def on_scale_change(self,event):
        if (float(self.scale.GetLineText(0)) < 1) and (float(self.scale.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale.GetLineText(0)))

    def on_xmax_change(self,event):
        if (float(self.xRangeMax.GetLineText(0)) < 600) and (float(self.xRangeMax.GetLineText(0)) > parameter_utils.get_x_range()[1]):
            parameter_utils.set_x_range(float(self.xRangeMax.GetLineText(0)),'max')
    
    def on_xmin_change(self,event):
        if (float(self.xRangeMin.GetLineText(0)) > 0) and (float(self.xRangeMin.GetLineText(0)) < parameter_utils.get_x_range()[0]):
            parameter_utils.set_x_range(float(self.xRangeMin.GetLineText(0)),'min')

    def on_ymax_change(self,event):
        if (float(self.yRangeMax.GetLineText(0)) < 15) and (float(self.yRangeMax.GetLineText(0)) > parameter_utils.get_y_range()[1]):
            parameter_utils.set_y_range(float(self.yRangeMax.GetLineText(0)),'max')

    def on_ymin_change(self,event):
        if (float(self.yRangeMin.GetLineText(0)) > -55) and (float(self.yRangeMin.GetLineText(0)) < parameter_utils.get_y_range()[0]):
            parameter_utils.set_y_range(float(self.yRangeMin.GetLineText(0)),'min')

    def on_check_line(self,event):
        if self.selectLine.IsChecked():
            parameter_utils.enable_help_line(True)
        else:
            parameter_utils.enable_help_line(False)
    
    def on_slide_line(self,event):
        parameter_utils.set_help_line(self.lineSlider.GetValue())

    def init_ranges(self):
        x_range = parameter_utils.get_x_range()
        y_range = parameter_utils.get_y_range()
        self.xRangeMax.SetValue(str(x_range[0]))
        self.xRangeMin.SetValue(str(x_range[1])) 
        self.yRangeMax.SetValue(str(y_range[0]))
        self.yRangeMin.SetValue(str(y_range[1]))
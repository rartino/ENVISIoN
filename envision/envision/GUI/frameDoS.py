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

        #Sizer for scale
        self.scaleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.scaleText = wx.StaticText(self.GetPane(),label="Scale: ")
        self.scale = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Scale1')
        self.scaleBox.Add(self.scaleText)
        self.scaleBox.Add(self.scale)

        self.scaleBox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.scaleText2 = wx.StaticText(self.GetPane(),label="Scale: ")
        self.scale2 = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Scale2')
        self.scaleBox2.Add(self.scaleText2)
        self.scaleBox2.Add(self.scale2)

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
        
        self.xRangeBox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.xRangeText2 = wx.StaticText(self.GetPane(),label="X Range: ")
        self.xRangeMax2 = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Max')
        self.xRangeMin2 = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Min')
        self.xRangeBox2.Add(self.xRangeText2)
        self.xRangeBox2.Add(self.xRangeMin2)
        self.xRangeBox2.Add(self.xRangeMax2)

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
        
        self.yRangeBox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.yRangeText2 = wx.StaticText(self.GetPane(),label="Y Range: ")
        self.yRangeMax2 = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Max')
        self.yRangeMin2 = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Min')
        self.yRangeBox2.Add(self.yRangeText2)
        self.yRangeBox2.Add(self.yRangeMin2)
        self.yRangeBox2.Add(self.yRangeMax2)

        #Help line setup
        self.selectLine = wx.CheckBox(self.GetPane(),label='Help line: ')
        self.lineSlider = wx.Slider(self.GetPane())

        self.selectLine2 = wx.CheckBox(self.GetPane(),label='Help line: ')
        self.lineSlider2 = wx.Slider(self.GetPane())

        #Add items in collapsible
        self.add_item(self.xRangeBox)
        self.add_item(self.yRangeBox)
        self.add_item(self.scaleBox)
        self.add_item(self.selectLine)
        self.add_item(self.lineSlider)
        self.add_item(self.xRangeBox2)
        self.add_item(self.yRangeBox2)
        self.add_item(self.scaleBox2)
        self.add_item(self.selectLine2)
        self.add_item(self.lineSlider2)

        #Bind signals
        self.scale.Bind(wx.EVT_TEXT_ENTER, self.on_scale_change)
        self.xRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_xmax_change)
        self.xRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_xmin_change)
        self.yRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_ymax_change)
        self.yRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_ymin_change)
        self.selectLine.Bind(wx.EVT_CHECKBOX, self.on_check_line)
        self.lineSlider.Bind(wx.EVT_SLIDER, self.on_slide_line)
        self.scale2.Bind(wx.EVT_TEXT_ENTER, self.on_scale_change2)
        self.xRangeMax2.Bind(wx.EVT_TEXT_ENTER, self.on_xmax_change2)
        self.xRangeMin2.Bind(wx.EVT_TEXT_ENTER, self.on_xmin_change2)
        self.yRangeMax2.Bind(wx.EVT_TEXT_ENTER, self.on_ymax_change2)
        self.yRangeMin2.Bind(wx.EVT_TEXT_ENTER, self.on_ymin_change2)
        self.selectLine2.Bind(wx.EVT_CHECKBOX, self.on_check_line2)
        self.lineSlider2.Bind(wx.EVT_SLIDER, self.on_slide_line2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    
    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable DoS vis
            parameter_utils.clear_processor_network()
        else:
            self.start_vis()

    def start_vis(self):
        if self.isPathEmpty():
            return    
        elif '/FermiEnergy' in  h5py.File(self.parent_collapsible.path, 'r')\
            and 'DOS' in  h5py.File(self.parent_collapsible.path, 'r'):
            #Start DoS vis
            self.open_message("When hitting ok, wait until both windows are fully loaded",
                            "Be patient!")
            envision.inviwo.dos(self.parent_collapsible.path, 
                                atom = 0, xpos = 0, ypos = 0)
            
            self.init_DoS()
            self.set_canvas_pos('DoS')
        else:
            self.open_message('The file of choice does not contain DoS-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()

    def init_DoS(self):
        x_range = parameter_utils.get_x_range('DOS Plotter')
        y_range = parameter_utils.get_y_range('DOS Plotter')
        x2_range = parameter_utils.get_x_range('DOS Plotter2')
        y2_range = parameter_utils.get_y_range('DOS Plotter2')
        self.xRangeMax.SetValue(str(x_range[0]))
        self.xRangeMin.SetValue(str(x_range[1])) 
        self.yRangeMax.SetValue(str(y_range[0]))
        self.yRangeMin.SetValue(str(y_range[1]))
        self.xRangeMax2.SetValue(str(x2_range[0]))
        self.xRangeMin2.SetValue(str(x2_range[1])) 
        self.yRangeMax2.SetValue(str(y2_range[0]))
        self.yRangeMin2.SetValue(str(y2_range[1]))
        self.scale.SetValue(str(parameter_utils.get_scale('DOS Plotter')))
        self.lineSlider.SetMax(parameter_utils.get_x_range('DOS Plotter')[0])
        self.lineSlider.SetMin(parameter_utils.get_x_range('DOS Plotter')[1])
        self.scale2.SetValue(str(parameter_utils.get_scale('DOS Plotter2')))
        self.lineSlider2.SetMax(parameter_utils.get_x_range('DOS Plotter2')[0])
        self.lineSlider2.SetMin(parameter_utils.get_x_range('DOS Plotter2')[1])
    
    #Control for scale, range and help line
    def on_scale_change(self,event):
        if (float(self.scale.GetLineText(0)) <= 1) and (float(self.scale.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale.GetLineText(0)), 'DOS Plotter')

    def on_scale_change2(self,event):
        if (float(self.scale2.GetLineText(0)) <= 1) and (float(self.scale2.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale2.GetLineText(0)), 'DOS Plotter2')

    def on_xmax_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMax.GetLineText(0)),'max', 'DOS Plotter')

    def on_xmax_change2(self,event):
        parameter_utils.set_x_range(float(self.xRangeMax2.GetLineText(0)),'max', 'DOS Plotter2')
    
    def on_xmin_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMin.GetLineText(0)),'min', 'DOS Plotter')

    def on_xmin_change2(self,event):
        parameter_utils.set_x_range(float(self.xRangeMin2.GetLineText(0)),'min', 'DOS Plotter2')

    def on_ymax_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMax.GetLineText(0)),'max', 'DOS Plotter')

    def on_ymax_change2(self,event):
        parameter_utils.set_y_range(float(self.yRangeMax2.GetLineText(0)),'max', 'DOS Plotter2')

    def on_ymin_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMin.GetLineText(0)),'min', 'DOS Plotter')

    def on_ymin_change2(self,event):
        parameter_utils.set_y_range(float(self.yRangeMin2.GetLineText(0)),'min', 'DOS Plotter2')

    def on_check_line(self,event):
        if self.selectLine.IsChecked():
            parameter_utils.enable_help_line(True, 'DOS Plotter')
        else:
            parameter_utils.enable_help_line(False, 'DOS Plotter')
    
    def on_check_line2(self,event):
        if self.selectLine2.IsChecked():
            parameter_utils.enable_help_line(True, 'DOS Plotter2')
        else:
            parameter_utils.enable_help_line(False, 'DOS Plotter2')

    def on_slide_line(self,event):
        parameter_utils.set_help_line(self.lineSlider.GetValue(), 'DOS Plotter')

    def on_slide_line2(self,event):
        parameter_utils.set_help_line(self.lineSlider2.GetValue(), 'DOS Plotter2')        

    
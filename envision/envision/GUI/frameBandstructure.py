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
        self.helpLine = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Help line value')

        #Grid lines and labels setup
        self.selectGrid = wx.CheckBox(self.GetPane(),label='Grid ')
        self.selectXLabel = wx.CheckBox(self.GetPane(),label='X label ')
        self.selectYLabel = wx.CheckBox(self.GetPane(),label='Y label ')
        self.gridWidth = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Grid width')
        self.selectLabel = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Label selection')

        #Add items
        self.add_item(self.xRangeBox)
        self.add_item(self.yRangeBox)
        self.add_item(self.scaleBox)
        self.add_item(self.selectLine)
        self.add_item(self.helpLine)
        self.add_item(self.selectGrid)
        self.add_item(self.gridWidth)
        self.add_item(self.selectXLabel)
        self.add_item(self.selectYLabel)
        self.add_item(self.selectLabel)
        

        self.scale.Bind(wx.EVT_TEXT_ENTER, self.on_scale_change)
        self.xRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_xmax_change)
        self.xRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_xmin_change)
        self.yRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_ymax_change)
        self.yRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_ymin_change)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)    
        self.selectLine.Bind(wx.EVT_CHECKBOX, self.on_check_line)
        self.selectGrid.Bind(wx.EVT_CHECKBOX, self.on_check_grid)
        self.gridWidth.Bind(wx.EVT_TEXT_ENTER, self.on_grid_change)
        self.selectXLabel.Bind(wx.EVT_CHECKBOX, self.on_check_x_label)
        self.selectYLabel.Bind(wx.EVT_CHECKBOX, self.on_check_y_label)
        self.selectLabel.Bind(wx.EVT_TEXT_ENTER, self.on_label_change)
        self.helpLine.Bind(wx.EVT_TEXT_ENTER, self.on_line_change)
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
            self.init_bandstructure()
            self.set_canvas_pos()
        else:
            self.open_message('The file of choice does not contain Bandstructure-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()

    def init_bandstructure(self):
        x_range = parameter_utils.get_x_range()
        y_range = parameter_utils.get_y_range()
        labels = parameter_utils.isEnabled_label()
        grid = parameter_utils.isEnable_grid()
        labelCount = parameter_utils.get_label()
        self.xRangeMax.SetValue(str(x_range[0]))
        self.xRangeMin.SetValue(str(x_range[1])) 
        self.yRangeMax.SetValue(str(y_range[0]))
        self.yRangeMin.SetValue(str(y_range[1]))
        self.scale.SetValue(str(parameter_utils.get_scale()))
        self.selectGrid.SetValue(grid)
        self.helpLine.SetValue(str(parameter_utils.get_help_line()))
        self.gridWidth.SetValue(str(parameter_utils.get_grid()))
        self.selectLabel.SetValue(str(labelCount))     
        if labels[0]:
            self.selectXLabel.SetValue(True)
        else:
            self.selectXLabel.SetValue(False)
        if labels[1]:
            self.selectYLabel.SetValue(True)
        else:
            self.selectYLabel.SetValue(False)

    def on_scale_change(self,event):
        if (float(self.scale.GetLineText(0)) <= 1) and (float(self.scale.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale.GetLineText(0)))

    def on_xmax_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMax.GetLineText(0)),'max')
    
    def on_xmin_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMin.GetLineText(0)),'min')

    def on_ymax_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMax.GetLineText(0)),'max')

    def on_ymin_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMin.GetLineText(0)),'min')

    def on_check_x_label(self,event):
        if self.selectXLabel.IsChecked():
            parameter_utils.enable_label(xLabel=True, processor='Line plot')
        else:
            parameter_utils.enable_label(xLabel=False, processor='Line plot')
    
    def on_check_y_label(self,event):
        if self.selectYLabel.IsChecked():
            parameter_utils.enable_label(yLabel=True, processor='Line plot')
        else:
            parameter_utils.enable_label(yLabel=False, processor='Line plot')

    def on_check_grid(self,event):
        if self.selectGrid.IsChecked():
            parameter_utils.enable_grid(gridBool=True, processor='Line plot')
        else:
            parameter_utils.enable_grid(gridBool=False, processor='Line plot')

    def on_check_line(self,event):
        if self.selectLine.IsChecked():
            parameter_utils.enable_help_line(True)
        else:
            parameter_utils.enable_help_line(False)
    
    def on_line_change(self,event):
        parameter_utils.set_help_line(float(self.helpLine.GetLineText(0)))
    
    def on_grid_change(self,event):
        parameter_utils.set_grid(float(self.gridWidth.GetLineText(0)), 'Line plot')
    
    def on_label_change(self,event):
        parameter_utils.set_label(round(float(self.selectLabel.GetLineText(0))), 'Line plot')

    
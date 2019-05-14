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
import wx,sys,os,inspect
import h5py
from generalCollapsible import GeneralCollapsible
import parameter_utils

path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir+"/../inviwo"))
import envision

class PCFFrame(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "PCF")
        
        #Sizer for scale
        self.scaleBox = wx.BoxSizer(wx.HORIZONTAL)
        self.scaleText = wx.StaticText(self.GetPane(),label="Scale: ")
        self.scale = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Scale1')
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

        #Help line setup
        self.selectLine = wx.CheckBox(self.GetPane(),label='Help line ')
        self.helpLine = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Help line value')

        #Grid lines and labels setup
        self.selectGrid = wx.CheckBox(self.GetPane(),label='Grid ')
        self.selectXLabel = wx.CheckBox(self.GetPane(),label='X label ')
        self.selectYLabel = wx.CheckBox(self.GetPane(),label='Y label ')
        self.gridText = wx.StaticText(self.GetPane(),label="Grid width: ")
        self.gridWidth = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Grid width')
        self.labelBox = wx.BoxSizer(wx.HORIZONTAL)
        self.labelText = wx.StaticText(self.GetPane(),label="Label count: ")
        self.labelSelect = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Label selection')
        self.labelBox.Add(self.labelText)
        self.labelBox.Add(self.labelSelect)

        #Y selection setup
        self.selectYBox = wx.BoxSizer(wx.HORIZONTAL)
        self.yLinesText = wx.StaticText(self.GetPane(),label="Y Seletion Range: ")
        self.enableYSelection = wx.CheckBox(self.GetPane(),label='Enable Y selection')
        self.ySelection = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Y selection')
        self.selectYBox.Add(self.yLinesText)
        self.selectYBox.Add(self.ySelection)
        self.enableYSelectionAll = wx.CheckBox(self.GetPane(),label='Enable all Y')
        
        #Setup for list for choosing Y
        self.listYText = wx.StaticText(self.GetPane(),label="List of Y:")
        self.listY = wx.Choice(self.GetPane(),choices=[])
        


         #Add items in collapsible
        self.add_item(self.xRangeBox)
        self.add_item(self.yRangeBox)
        self.add_item(self.scaleBox)
        self.add_item(self.selectLine)
        self.add_item(self.helpLine)
        self.add_item(self.selectGrid)
        self.add_item(self.gridText)
        self.add_item(self.gridWidth)
        self.add_item(self.selectXLabel)
        self.add_item(self.selectYLabel)
        self.add_item(self.labelBox)
        self.add_item(self.enableYSelectionAll)
        self.add_item(self.enableYSelection)
        self.add_item(self.listYText)
        self.add_item(self.listY)
        self.add_item(self.selectYBox)

        #Bind signals
        self.scale.Bind(wx.EVT_TEXT_ENTER, self.on_scale_change)
        self.xRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_xmax_change)
        self.xRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_xmin_change)
        self.yRangeMax.Bind(wx.EVT_TEXT_ENTER, self.on_ymax_change)
        self.yRangeMin.Bind(wx.EVT_TEXT_ENTER, self.on_ymin_change)
        self.selectLine.Bind(wx.EVT_CHECKBOX, self.on_check_line)
        self.helpLine.Bind(wx.EVT_TEXT_ENTER, self.on_line_change)
        self.selectGrid.Bind(wx.EVT_CHECKBOX, self.on_check_grid)
        self.gridWidth.Bind(wx.EVT_TEXT_ENTER, self.on_grid_change)
        self.selectXLabel.Bind(wx.EVT_CHECKBOX, self.on_check_x_label)
        self.selectYLabel.Bind(wx.EVT_CHECKBOX, self.on_check_y_label)
        self.labelSelect.Bind(wx.EVT_TEXT_ENTER, self.on_label_change)
        self.enableYSelection.Bind(wx.EVT_CHECKBOX, self.on_check_enableYselection)
        self.listY.Bind(wx.EVT_CHOICE, self.on_list_select)
        self.enableYSelectionAll.Bind(wx.EVT_CHECKBOX, self.on_check_enableYselectionAll)
        self.ySelection.Bind(wx.EVT_TEXT_ENTER, self.on_ySelection_change)

        # Override default binding
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)

    def on_collapse(self, event = None):
        self.update_collapse()
        # Needs to be called to update the layout properly
        if self.IsCollapsed():
            # Disable vis
            parameter_utils.clear_processor_network()
            print("Not paircorr")
        else:
            #Start vis
            self.start_vis()
            print("Paircorr")

    def start_vis(self):
        if self.isPathEmpty():
            return
        elif "/PairCorrelationFunc" in  h5py.File(self.parent_collapsible.path, 'r'):
            #Start vis
            envision.inviwo.paircorrelation(self.parent_collapsible.path, xpos=0, ypos=0)
            self.set_canvas_pos('PCF')
            self.init_PCF()
        else:
            self.open_message('The file of choice does not contain PCF-data',
                                'Visualization failed!')
            self.Collapse(True)
            self.update_collapse()     
        
    def init_PCF(self):
        x_range = parameter_utils.get_x_range("pair correlation plotter")
        y_range = parameter_utils.get_y_range("pair correlation plotter")
        labels = parameter_utils.isEnabled_label("pair correlation plotter")
        grid = parameter_utils.isEnable_grid("pair correlation plotter")
        labelCount = parameter_utils.get_label("pair correlation plotter")
        multipleYBool = parameter_utils.isEnabled_multiple_y('pair correlation plotter')
        ySelect = parameter_utils.get_yline_range('pair correlation plotter')
        allYSelect = parameter_utils.isEnabled_all_y('pair correlation plotter')
        pcfIndex = parameter_utils.get_choosen_line('pair correlation plotter')
        self.xRangeMax.SetValue(str(x_range[0]))
        self.xRangeMin.SetValue(str(x_range[1])) 
        self.yRangeMax.SetValue(str(y_range[0]))
        self.yRangeMin.SetValue(str(y_range[1]))
        self.scale.SetValue(str(parameter_utils.get_scale("pair correlation plotter")))
        self.selectGrid.SetValue(grid)
        self.ySelection.SetValue(ySelect)
        self.helpLine.SetValue(str(parameter_utils.get_help_line("pair correlation plotter")))
        self.gridWidth.SetValue(str(parameter_utils.get_grid("pair correlation plotter")))
        self.labelSelect.SetValue(str(labelCount))       
        if labels[0]:
            self.selectXLabel.SetValue(True)
        else:
            self.selectXLabel.SetValue(False)
        if labels[1]:
            self.selectYLabel.SetValue(True)
        else:
            self.selectYLabel.SetValue(False) 
        if multipleYBool:
            self.enableYSelection.SetValue(True)
        else:
            self.enableYSelection.SetValue(False)
        if allYSelect:
            self.enableYSelectionAll.SetValue(True)
        else:
            self.enableYSelectionAll.SetValue(False)
        self.sizer.Hide(self.selectYBox)
        #Init list of Y
        self.set_Y_list()
        self.listY.SetSelection(pcfIndex)
    
    #Control for scale, range and help line
    def on_scale_change(self,event):
        if (float(self.scale.GetLineText(0)) <= 1) and (float(self.scale.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale.GetLineText(0)), "pair correlation plotter")

    def on_xmax_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMax.GetLineText(0)),'max', "pair correlation plotter")

    def on_xmin_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMin.GetLineText(0)),'min', "pair correlation plotter")

    def on_ymax_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMax.GetLineText(0)),'max', "pair correlation plotter")

    def on_ymin_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMin.GetLineText(0)),'min', "pair correlation plotter")

    def on_check_line(self,event):
        if self.selectLine.IsChecked():
            parameter_utils.enable_help_line(True, "pair correlation plotter")
        else:
            parameter_utils.enable_help_line(False, "pair correlation plotter")

    def on_check_x_label(self,event):
        if self.selectXLabel.IsChecked():
            parameter_utils.enable_label(xLabel=True, processor="pair correlation plotter")
        else:
            parameter_utils.enable_label(xLabel=False, processor="pair correlation plotter")
    
    def on_check_y_label(self,event):
        if self.selectYLabel.IsChecked():
            parameter_utils.enable_label(yLabel=True, processor="pair correlation plotter")
        else:
            parameter_utils.enable_label(yLabel=False, processor="pair correlation plotter")

    def on_check_grid(self,event):
        if self.selectGrid.IsChecked():
            parameter_utils.enable_grid(gridBool=True, processor="pair correlation plotter")
        else:
            parameter_utils.enable_grid(gridBool=False, processor="pair correlation plotter")

    def on_line_change(self,event):
        parameter_utils.set_help_line(float(self.helpLine.GetLineText(0)), "pair correlation plotter")
    
    def on_grid_change(self,event):
        parameter_utils.set_grid(float(self.gridWidth.GetLineText(0)), "pair correlation plotter")
    
    def on_label_change(self,event):
        enteredNum = int(self.labelSelect.GetLineText(0))
        if (enteredNum >= 0):
            parameter_utils.set_label(enteredNum, "pair correlation plotter")
    
    def on_check_enableYselection(self,event):
        if self.enableYSelection.IsChecked():
            parameter_utils.enable_multiple_y(multipleBool=True, processor='pair correlation plotter')
            self.sizer.Show(self.selectYBox)
        else:
            parameter_utils.enable_multiple_y(multipleBool=False, processor='pair correlation plotter')
            self.sizer.Hide(self.selectYBox)
        self.update_collapse()

    def on_check_enableYselectionAll(self,event):
        if self.enableYSelectionAll.IsChecked():
            parameter_utils.enable_all_y(multipleBool=True, processor='pair correlation plotter')
        else:
            parameter_utils.enable_all_y(multipleBool=False, processor='pair correlation plotter')
    
    def on_ySelection_change(self,event):
        num = None
        if ':' in self.ySelection.GetLineText(0):
            if ',' in self.ySelection.GetLineText(0):
                choiceList = self.ySelection.GetLineText(0).split(':')
                choice = []
                for part in choiceList:
                    choice.extend(part.split(','))
            else:
                choice = self.ySelection.GetLineText(0).split(':')
        elif ',' in self.ySelection.GetLineText(0):
            choice = self.ySelection.GetLineText(0).split(',')
        else:
            num = self.ySelection.GetLineText(0)
        append = False
        if num == None:
            for number in choice:
                if (int(number) < len(self.listY.GetItems())) and (int(number) >= 0):
                    append = True
                else:
                    append = False
            if append:
                parameter_utils.set_yline_range(self.ySelection.GetLineText(0),'pair correlation plotter')
        else:
            if (int(num) < len(self.listY.GetItems())) and (int(num) >= 0):
                    parameter_utils.set_yline_range(num,'pair correlation plotter')
        

    def on_list_select(self,event):
        index = self.listY.GetCurrentSelection()
        if (index >= 0) and (index < len(self.listY.GetItems())):
            parameter_utils.choose_line(index,'pair correlation plotter')
        
    def set_Y_list(self):
        self.listY.Clear()
        self.listY.Set(parameter_utils.get_option_list('pair correlation plotter'))


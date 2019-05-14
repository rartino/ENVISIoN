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
        self.enableYSelection = wx.CheckBox(self.GetPane(),label='Enable Y selection')
        self.selectYBox = wx.BoxSizer(wx.HORIZONTAL)
        self.yLinesText = wx.StaticText(self.GetPane(),label="Y Seletion Range: ")
        self.ySelection = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Y selection')
        self.selectYBox.Add(self.yLinesText)
        self.selectYBox.Add(self.ySelection)
        self.enableYSelectionAll = wx.CheckBox(self.GetPane(),label='Enable all Y')
        self.selectPartialBox = wx.BoxSizer(wx.HORIZONTAL)
        self.partialText = wx.StaticText(self.GetPane(),label="Partial choice:")
        self.partialChoice = wx.TextCtrl(self.GetPane(), style=wx.TE_PROCESS_ENTER,
                                     name='Partial choice')
        self.selectPartialBox.Add(self.partialText)
        self.selectPartialBox.Add(self.partialChoice)
        
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
        self.add_item(self.listYText)
        self.add_item(self.listY)
        self.add_item(self.selectPartialBox)
        self.add_item(self.enableYSelectionAll)
        self.add_item(self.enableYSelection)
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
        self.ySelection.Bind(wx.EVT_TEXT_ENTER, self.on_ySelection_change)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse)
        self.enableYSelectionAll.Bind(wx.EVT_CHECKBOX, self.on_check_enableYselectionAll)
        self.partialChoice.Bind(wx.EVT_TEXT_ENTER, self.on_change_partial)

    
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
        labels = parameter_utils.isEnabled_label('DOS Plotter')
        grid = parameter_utils.isEnable_grid('DOS Plotter')
        multipleYBool = parameter_utils.isEnabled_multiple_y('DOS Plotter')
        ySelect = parameter_utils.get_yline_range('DOS Plotter')
        allYSelect = parameter_utils.isEnabled_all_y('DOS Plotter')
        partial = parameter_utils.get_partial_value('Partial Pick')
        labelCount = parameter_utils.get_label('DOS Plotter')
        self.xRangeMax.SetValue(str(x_range[0]))
        self.xRangeMin.SetValue(str(x_range[1])) 
        self.yRangeMax.SetValue(str(y_range[0]))
        self.yRangeMin.SetValue(str(y_range[1]))
        self.scale.SetValue(str(parameter_utils.get_scale('DOS Plotter')))
        self.selectGrid.SetValue(grid)
        self.helpLine.SetValue(str(parameter_utils.get_help_line('DOS Plotter')))
        self.gridWidth.SetValue(str(parameter_utils.get_grid('DOS Plotter')))
        self.ySelection.SetValue(ySelect)
        self.labelSelect.SetValue(str(labelCount))
        self.partialChoice.SetValue(str(partial))        
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
        self.set_Y_list(partial)
    
    #Control for scale, range and help line
    def on_scale_change(self,event):
        if (float(self.scale.GetLineText(0)) <= 1) and (float(self.scale.GetLineText(0)) > 0):
            parameter_utils.change_scale(float(self.scale.GetLineText(0)), 'DOS Plotter')

    def on_xmax_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMax.GetLineText(0)),'max', 'DOS Plotter')

    def on_xmin_change(self,event):
        parameter_utils.set_x_range(float(self.xRangeMin.GetLineText(0)),'min', 'DOS Plotter')

    def on_ymax_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMax.GetLineText(0)),'max', 'DOS Plotter')

    def on_ymin_change(self,event):
        parameter_utils.set_y_range(float(self.yRangeMin.GetLineText(0)),'min', 'DOS Plotter')

    def on_check_line(self,event):
        if self.selectLine.IsChecked():
            parameter_utils.enable_help_line(True, 'DOS Plotter')
        else:
            parameter_utils.enable_help_line(False, 'DOS Plotter')

    def on_check_x_label(self,event):
        if self.selectXLabel.IsChecked():
            parameter_utils.enable_label(xLabel=True, processor='DOS Plotter')
        else:
            parameter_utils.enable_label(xLabel=False, processor='DOS Plotter')
    
    def on_check_y_label(self,event):
        if self.selectYLabel.IsChecked():
            parameter_utils.enable_label(yLabel=True, processor='DOS Plotter')
        else:
            parameter_utils.enable_label(yLabel=False, processor='DOS Plotter')

    def on_check_grid(self,event):
        if self.selectGrid.IsChecked():
            parameter_utils.enable_grid(gridBool=True, processor='DOS Plotter')
        else:
            parameter_utils.enable_grid(gridBool=False, processor='DOS Plotter')

    def on_line_change(self,event):
        parameter_utils.set_help_line(float(self.lineSlider.GetLineText(0)), 'DOS Plotter')
    
    def on_grid_change(self,event):
        parameter_utils.set_grid(float(self.gridSlider.GetLineText(0)), 'DOS Plotter')
    
    def on_label_change(self,event):
        enteredNum = int(self.labelSelect.GetLineText(0))
        if (enteredNum >= 0):
            parameter_utils.set_label(enteredNum, 'DOS Plotter')

    def on_change_partial(self,event):
        parameter_utils.set_partial_value(round(float(self.partialChoice.GetLineText(0))), 'Partial Pick')
        self.set_Y_list(parameter_utils.get_partial_value('Partial Pick'))

    def on_check_enableYselection(self,event):
        if self.enableYSelection.IsChecked():
            parameter_utils.enable_multiple_y(multipleBool=True, processor='DOS Plotter')
            self.sizer.Show(self.selectYBox)
        else:
            parameter_utils.enable_multiple_y(multipleBool=False, processor='DOS Plotter')
            self.sizer.Hide(self.selectYBox)
        self.update_collapse()

    def on_check_enableYselectionAll(self,event):
        if self.enableYSelectionAll.IsChecked():
            parameter_utils.enable_all_y(multipleBool=True, processor='DOS Plotter')
        else:
            parameter_utils.enable_all_y(multipleBool=False, processor='DOS Plotter')

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
                parameter_utils.set_yline_range(self.ySelection.GetLineText(0),'DOS Plotter')
        else:
            if (int(num) < len(self.listY.GetItems())) and (int(num) >= 0):
                    parameter_utils.set_yline_range(num,'DOS Plotter')

    def set_Y_list(self,partial=0):
        with h5py.File(self.parent_collapsible.path, 'r') as file:
            self.listY.Clear()
            counter = 0
            for key in file.get("DOS").get("Total").keys():
                if key != 'Energy':
                    if '(dwn)' in key:
                        self.listY.Append(str(counter)+': '+'Total '+key)
                        counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if '(dwn)' in key:
                    if ('x2' in key) or ('y2' in key) or ('z2' in key):
                        self.listY.Append(str(counter)+': '+'Total '+key)
                        counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(dwn)' in key) and (('(x)' in key) or ('(y)' in key)):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(dwn)' in key) and ('(xy)' in key):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(dwn)' in key) and ('(z)' in key):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(dwn)' in key) and (('(xz)' in key) or ('(yz)' in key)):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Total").keys():
                if key != 'Energy':
                    if '(up)' in key:
                        self.listY.Append(str(counter)+': '+'Total '+key)
                        counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if '(up)' in key:
                    if ('x2' in key) or ('y2' in key) or ('z2' in key):
                        self.listY.Append(str(counter)+': '+'Total '+key)
                        counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(up)' in key) and (('(x)' in key) or ('(y)' in key)):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(up)' in key) and ('(xy)' in key):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(up)' in key) and ('(z)' in key):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1
            for key in file.get("DOS").get("Partial").get(str(partial)).keys():
                if ('(up)' in key) and (('(xz)' in key) or ('(yz)' in key)):
                    self.listY.Append(str(counter)+': '+key)
                    counter += 1

    
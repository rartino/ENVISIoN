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

"""*****************************************************************************"""
"""This file sets up the Parser-section of the GUI, which is a collapsible pane."""
"""*****************************************************************************"""

import wx, sys, os
import inspect
path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir+'/../'))
sys.path.insert(0, os.path.expanduser(path_to_current_dir+'/../parser/vasp'))
from bandstructure import bandstructure
from doscar import dos
from md import md
from unitcell import unitcell
from volume import charge, elf
from fermi import fermi_surface
from parchg import parchg
from PCF import paircorrelation
from fermiEnergy import fermi_energy
from main import *
from generalCollapsible import GeneralCollapsible

class ParserPane(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Parser")

    #Path-selection to file for parsing
        self.fileText = wx.StaticText(self.GetPane(),
                                    label="Directory with files to parse:")
        self.chooseParseDir = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select dir'))
        self.enterPath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
    #Path-selection to dir for saving
        self.dirText = wx.StaticText(self.GetPane(),
                                    label="Save new file in directory:")       
        self.chooseSaveDir = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select dir'))
        self.enterSavePath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
    #Path-selection to existing file for saving
        self.existFileText = wx.StaticText(self.GetPane(),
                                    label="Or save in existing .hdf5 file:")       
        self.chooseSaveFile = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterSaveFile = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
    #Visualization-type selection:
        self.typeText = wx.StaticText(self.GetPane(),
                                    label="Type of Visualization:")
        self.selectVis = wx.ComboBox(self.GetPane(), size=self.itemSize,
                                    value = "Select type",
                                    choices= ('All', 'Bandstructure', 'Charge',
                                            'DoS', 'ELF', 'Fermi energy',
                                            'MD', 'Parchg', 'PCF',
                                            'Unitcell'))
        self.parserDict = {
            'Unitcell' : 'unitcell from VASP' ,
            'MD' : 'molecular dynamics from VASP',
            'Charge' : 'charge from VASP',
            'ELF' : 'ELF from VASP',
            'DoS' : 'DOS from VASP',
            'Bandstructure' : 'bandstructure from VASP',
            'PCF' : 'PCF from VASP',
            'Parchg' : 'Parchg from VASP',
            'Fermi energy': 'Fermi energy from VASP'
        }

        self.parseFuncDict = {
        'Unitcell': unitcell,
        'MD': md,
        'Charge': charge,
        'ELF': elf,
        'DoS': dos,
        'Bandstructure': bandstructure,
        'PCF' : paircorrelation,
        'Parchg' : parchg,
        'Fermi energy': fermi_energy
    }

    #Parse-button
        self.hdf5Text = wx.StaticText(self.GetPane(),
                                    label="Enter new filename:")
        self.hdf5File = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="(without .hdf5)",
                                    style=wx.TE_PROCESS_ENTER)
        self.parse = wx.Button(self.GetPane(), size=self.itemSize,
                                label = str('Parse'))

    #Text colour settings
        self.fileText.SetForegroundColour(self.text_colour)
        self.dirText.SetForegroundColour(self.text_colour)
        self.typeText.SetForegroundColour(self.text_colour)
        self.existFileText.SetForegroundColour(self.text_colour)

    #Variables for paths, type of Visualization and parsing.
        self.path = ""
        self.savePath = ""
        self.visType = 'All'
        self.newFileHdf5 = "NewFile"
        self.hdf5Path = ''
        self.parseOut = None
        self.isFileSelected = False
        
    #Item-addition in pane
        expand_flag = wx.SizerFlags().Expand().Border(wx.ALL, 1)
        self.add_item(self.fileText, sizer_flags=expand_flag)
        self.add_item(self.enterPath, sizer_flags=expand_flag)
        self.add_item(self.chooseParseDir,sizer_flags=expand_flag)
        self.add_item(self.dirText, sizer_flags=expand_flag)
        self.add_item(self.enterSavePath, sizer_flags=expand_flag)
        self.add_item(self.chooseSaveDir,sizer_flags=expand_flag)
        self.add_item(self.existFileText,sizer_flags=expand_flag)
        self.add_item(self.enterSaveFile,sizer_flags=expand_flag)
        self.add_item(self.chooseSaveFile,sizer_flags=expand_flag)
        self.add_item(self.typeText, sizer_flags=expand_flag)
        self.add_item(self.selectVis,sizer_flags=expand_flag)
        self.add_item(self.hdf5Text,sizer_flags=expand_flag)
        self.add_item(self.hdf5File,sizer_flags=expand_flag)
        self.add_item(self.parse,sizer_flags=expand_flag)
        
    #Signal-handling for buttons and boxes:
        self.chooseParseDir.Bind(wx.EVT_BUTTON,self.dir_pressed)
        self.enterPath.Bind(wx.EVT_TEXT_ENTER,self.path_OnEnter)
        self.chooseSaveDir.Bind(wx.EVT_BUTTON,self.parse_selected)
        self.enterSavePath.Bind(wx.EVT_TEXT_ENTER,self.savePath_OnEnter)
        self.enterSaveFile.Bind(wx.EVT_TEXT_ENTER,self.saveFile_OnEnter)
        self.chooseSaveFile.Bind(wx.EVT_BUTTON,self.file_select)
        self.selectVis.Bind(wx.EVT_COMBOBOX,self.vis_selected)
        self.parse.Bind(wx.EVT_BUTTON,self.parse_pressed)
        self.hdf5File.Bind(wx.EVT_TEXT, self.hdf5_name_enter)
        
#When "File to parse"-select button is pressed
    def dir_pressed(self,event):
        self.path = self.choose_directory("Choose directory with files to parse")
        if '\\' in self.path:
            self.path = self.path.replace('\\','/')
        if not self.path == "":
            self.enterPath.SetValue(self.path)

#When path entered in text and Enter-key is pressed
    def path_OnEnter(self,event):
        self.path = self.directory_if_exists(self.enterPath.GetLineText(0))
        if '\\' in self.path:
            self.path = self.path.replace('\\','/')

#When "Save in dir"-select button is pressed
    def parse_selected(self,event):
        self.savePath = self.choose_directory("Choose output directory")
        if '\\' in self.savePath:
            self.savePath = self.savePath.replace('\\','/')
        if not self.savePath == "":
            self.enterSavePath.SetValue(self.savePath)
        self.isFileSelected = False
    
    def file_select(self,event):
        self.savePath = self.choose_file()
        if '\\' in self.savePath:
            self.savePath = self.savePath.replace('\\','/')
        if not self.savePath == "":
            self.enterSaveFile.SetValue(self.savePath)
            self.isFileSelected = True
        else:
            self.isFileSelected = False


#When save-path entered in text and Enter-key is pressed
    def savePath_OnEnter(self,event):
        self.savePath = self.directory_if_exists(self.enterSavePath.GetLineText(0))
        if '\\' in self.savePath:
            self.savePath = self.savePath.replace('\\','/')
        self.isFileSelected = False

    def saveFile_OnEnter(self,event):
        self.savePath = self.directory_if_exists(self.enterSavePath.GetLineText(0))
        if '\\' in self.savePath:
            self.savePath = self.savePath.replace('\\','/')
        if os.path.exists(self.savePath):
            self.isFileSelected = True
        else:
            self.isFileSelected = False
        

#When visualization-type is changed
    def vis_selected(self,event):
        self.visType = self.selectVis.GetValue()

#Select the hdf5 file name:
    def hdf5_name_enter(self,event):
        self.newFileHdf5 = self.hdf5File.GetLineText(0)

#When Parse-button is pressed
    def parse_pressed(self,event):
    #Parse with suitable function
        if self.visType == 'All':
            if self.isFileSelected:
                self.parseOut = parse_all(self.savePath, self.path)
            else:
                self.parseOut = parse_all(self.savePath+'/'+self.newFileHdf5+'.hdf5', self.path)
        elif self.isFileSelected: 
            if self.parseFuncDict[self.visType](self.savePath, self.path):
                self.open_message("Parsing "+self.path+
                                " successfully done for "+
                                self.visType+" visualization!",
                                "Succsessfully parsed!")
            return
        elif self.parseFuncDict[self.visType](self.savePath+'/'+self.newFileHdf5+'.hdf5', self.path):
            self.open_message("Parsing "+self.path+
                                " successfully done for "+
                                self.visType+" visualization!",
                                "Succsessfully parsed!")
            
            return            
    #Check output and put out appropriate message
        #Parse failed:     
        if self.parseOut == None:
            self.open_message("Parsing "+self.path+" failed!",
                        "Failed!")
        #All parsing skipped
        elif not self.parseOut:
            self.open_message("Nothing new to parse!",
                        "Failed!")
        #Possible parsings completed
        else:
            self.open_message("Parsing "+self.path+
                                " successfully done for: "+
                                ', '.join(self.parseOut),
                                "Succsessfully parsed!")
#Return path if the path exists.                        
    def directory_if_exists(self,path):
        if not os.path.exists(path):
            self.open_message(path+" not a valid directory!","Failed!")
            return ""
        else: 
            return path

#Dialog for choosing file in file explorer
    def choose_directory(self,label):
        dirFrame = wx.Frame(None, -1, 'win.py')
        dirFrame.SetSize(0,0,200,50)
        dirDialog = wx.DirDialog(dirFrame, label,
                                 "", style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        dirDialog.ShowModal()
        path = dirDialog.GetPath()
        dirDialog.Destroy()
        dirFrame.Destroy()
        return path

    def choose_file(self):
        fileFrame = wx.Frame(None, -1, 'win.py')
        fileFrame.SetSize(0,0,200,50)
        fileDialog = wx.FileDialog(fileFrame, "Open", "", "", 
                                      "HDF5 files (*.hdf5)|*.hdf5", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDialog.ShowModal()
        path = fileDialog.GetPath()
        fileDialog.Destroy()
        fileFrame.Destroy()
        return path

#Dialog for messages, fail or successes
    def open_message(self,message,label):
        messageFrame = wx.Frame(None, -1, 'win.py')
        messageFrame.SetSize(0,0,60,50)
        messageFrame.Centre()
        pathDialog = wx.MessageDialog(messageFrame, message, 
                                        label, wx.FD_OPEN)
        #Show dialog
        pathDialog.ShowModal()
        pathDialog.Destroy()
        messageFrame.Destroy()


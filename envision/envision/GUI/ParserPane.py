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
"""This file sets up the Parser-section of the GUI, which is a collapsible pane."""
"""*****************************************************************************"""


import wx, sys, os

# sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision/envision/"))
#from main import *
from generalCollapsible import GeneralCollapsible

class ParserPane(GeneralCollapsible):
    def __init__(self, parent):
        super().__init__(parent, "Parser")

    #Path-selection to file for parsing
        self.fileText = wx.StaticText(self.GetPane(),
                                    label="File to parse:")
        self.chooseFile = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterPath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
    #Path-selection to folder for saving
        self.folderText = wx.StaticText(self.GetPane(),
                                    label="Save in folder:")       
        self.chooseFolder = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterSavePath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
    #Visualization-type selection:
        self.typeText = wx.StaticText(self.GetPane(),
                                    label="Type of Visualization:")
        self.selectVis = wx.ComboBox(self.GetPane(), size=self.itemSize,
                                    value = "Select type",
                                    choices= ("ELF","DOS","PCF"))

    #Parse-button
        self.parse = wx.Button(self.GetPane(), size=self.itemSize,
                                label = str('Parse'))

    #Text colour settings
        self.fileText.SetForegroundColour(self.text_colour)
        self.folderText.SetForegroundColour(self.text_colour)
        self.typeText.SetForegroundColour(self.text_colour)

    #Variables for paths, type of Visualization and parsing.
        self.path = ""
        self.savePath = ""
        self.visType = ""
        self.parseOut = None
        
    #Item-addition in pane
        expand_flag = wx.SizerFlags().Expand().Border(wx.ALL, 1)
        self.add_item(self.fileText, sizer_flags=expand_flag)
        self.add_item(self.enterPath, sizer_flags=expand_flag)
        self.add_item(self.chooseFile,sizer_flags=expand_flag)
        self.add_item(self.folderText, sizer_flags=expand_flag)
        self.add_item(self.enterSavePath, sizer_flags=expand_flag)
        self.add_item(self.chooseFolder,sizer_flags=expand_flag)
        self.add_item(self.typeText, sizer_flags=expand_flag)
        self.add_item(self.selectVis,sizer_flags=expand_flag)
        self.add_item(self.parse,sizer_flags=expand_flag)
        
    #Signal-handling for buttons and boxes:
        self.chooseFile.Bind(wx.EVT_BUTTON,self.file_pressed)
        self.enterPath.Bind(wx.EVT_TEXT_ENTER,self.path_OnEnter)
        self.chooseFolder.Bind(wx.EVT_BUTTON,self.parse_selected)
        self.enterSavePath.Bind(wx.EVT_TEXT_ENTER,self.savePath_OnEnter)
        self.selectVis.Bind(wx.EVT_COMBOBOX,self.vis_selected)
        self.parse.Bind(wx.EVT_BUTTON,self.parse_pressed)
        
#When "File to parse"-select button is pressed
    def file_pressed(self,event):
        self.path = self.choose_file("Choose directory with files to parse")
        self.enterPath.SetValue(self.path)

#When path entered in text and Enter-key is pressed
    def path_OnEnter(self,event):
        self.path = self.directory_if_exists(self.enterPath.GetLineText(0))

#When "Save in folder"-select button is pressed
    def parse_selected(self,event):
        self.savePath = self.choose_file("Choose output directory")
        self.enterSavePath.SetValue(self.savePath)
    
#When save-path entered in text and Enter-key is pressed
    def savePath_OnEnter(self,event):
        self.savePath = self.directory_if_exists(self.enterSavePath.GetLineText(0))

#When visualization-type is changed
    def vis_selected(self,event):
        self.visType = self.selectVis.GetValue()
    
#When Parse-button is pressed
    def parse_pressed(self,event):
    #self.parseOut = parse_all(self.savePath,self.path)
        if not self.parseOut == None:
            self.open_message("Parsing "+self.path+" successfully done!",
                        "Succsessfully parsed!")
        else:
            self.open_message("Parsing "+self.path+" failed!",
                        "Failed!")

#Return path if the path exists.                        
    def directory_if_exists(self,path):
        if not os.path.exists(path):
            self.open_message(path+" not a valid directory!","Failed!")
            return ""
        else: 
            return path

#Dialog for choosing file in file explorer
    def choose_file(self,label):
        dirFrame = wx.Frame(None, -1, 'win.py')
        dirFrame.SetSize(0,0,200,50)
        dirDialog = wx.DirDialog(dirFrame, label,
                                 "", style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        dirDialog.ShowModal()
        path = dirDialog.GetPath()
        dirDialog.Destroy()
        dirFrame.Destroy()
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
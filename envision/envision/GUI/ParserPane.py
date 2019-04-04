import wx, sys, os

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision/envision/"))
#from main import *
class ParserPane(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #Collpane-style:
        self.bg_colour = wx.Colour(76,75,77)
        self.text_colour = wx.Colour(255,255,255)
        self.SetBackgroundColour(self.bg_colour)
        self.itemSize = wx.Size(150,25)

        #Path-selection to file for parsing
        self.fileText = wx.StaticText(self.GetPane(),
                                    label="File to parse:")
        self.fileText.SetForegroundColour(self.text_colour)                                    
        self.path = ""
        self.chooseFile = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterPath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)

        #Path-selection to folder for saving
        self.folderText = wx.StaticText(self.GetPane(),
                                    label="Save in folder:")
        self.folderText.SetForegroundColour(self.text_colour)                                    
        self.savePath = ""
        self.chooseFolder = wx.Button(self.GetPane(), size=self.itemSize,
                                    label = str('..or select file'))
        self.enterSavePath = wx.TextCtrl(self.GetPane(), size=self.itemSize,
                                    value="Enter path..",
                                    style=wx.TE_PROCESS_ENTER)
        
        #Visualization-type selection:
        self.typeText = wx.StaticText(self.GetPane(),
                                    label="Type of Visualization:")
        self.typeText.SetForegroundColour(self.text_colour)
        self.visType = ""
        self.selectVis = wx.ComboBox(self.GetPane(), size=self.itemSize,
                                    value = "Select type",
                                    choices= ("ELF","DOS","PKF"))

        #Execute parser
        self.parseOut = None
        self.parse = wx.Button(self.GetPane(), size=self.itemSize,
                                label = str('Parse'))

        #Item-addition in pane:
        sizer.Add(self.fileText, wx.GROW,1)
        sizer.Add(self.enterPath, wx.GROW,1)
        sizer.Add(self.chooseFile,wx.GROW,1)
        sizer.Add(self.folderText, wx.GROW,1)
        sizer.Add(self.enterSavePath, wx.GROW,1)
        sizer.Add(self.chooseFolder,wx.GROW,1)
        sizer.Add(self.typeText, wx.GROW,1)
        sizer.Add(self.selectVis,wx.GROW,1)
        sizer.Add(self.parse,wx.GROW,1)
        
        #Signal-handling for buttons:
        self.chooseFile.Bind(wx.EVT_BUTTON,self.file_pressed)
        self.enterPath.Bind(wx.EVT_TEXT_ENTER,self.path_OnEnter)
        self.chooseFolder.Bind(wx.EVT_BUTTON,self.folder_pressed)
        self.enterSavePath.Bind(wx.EVT_TEXT_ENTER,self.savePath_OnEnter)
        self.selectVis.Bind(wx.EVT_COMBOBOX,self.vis_selected)
        self.parse.Bind(wx.EVT_BUTTON,self.parse_pressed)
        self.GetPane().SetSizer(sizer)
        
    
    #When file-explorer button is pressed
    def file_pressed(self,event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0,0,200,50)
        openFileDialog = wx.DirDialog(frame, "Choose directory with files to parse", "", 
                                       style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        #openFileDialog = wx.FileDialog(frame, "Open", "", "", 
        #                              "Text files (*.txt)|*.txt", 
        #                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.path = openFileDialog.GetPath()
        openFileDialog.Destroy()
    
    #When path entered in text and Enter-key is pressed
    def path_OnEnter(self,event):
        self.path = self.enterPath.GetLineText()

    #When file-explorer button is pressed
    def folder_pressed(self,event):
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0,0,200,50)
        openFolderDialog = wx.DirDialog(frame, "Choose output directory", "", 
                                       style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        openFolderDialog.ShowModal()
        self.savePath = openFolderDialog.GetPath()
        openFolderDialog.Destroy()
    
    #When path entered in text and Enter-key is pressed
    def savePath_OnEnter(self,event):
        self.savePath = self.enterSavePath.GetLineText()

    #When visualization-type is changed
    def vis_selected(self,event):
        self.visType = self.selectVis.GetValue()
    
    #When Parse-button is pressed
    def parse_pressed(self,event):
        #self.parseOut = parse_all(self.savePath,self.path)
        frame = wx.Frame(None, -1, 'win.py')
        frame.SetDimensions(0,0,60,50)
        frame.Centre()
        if not self.parseOut == None:
            parseDialog = wx.MessageDialog(frame,  
                                        "Parsing "+self.path+" successfully done!",
                                        "Succsessfully parsed!", 
                                        wx.FD_OPEN)
            
        else:
            parseDialog = wx.MessageDialog(frame,  
                                        "Parsing "+self.path+" failed!",
                                        "Failed!", 
                                        wx.FD_OPEN)
        parseDialog.ShowModal()
        parseDialog.Destroy()
        


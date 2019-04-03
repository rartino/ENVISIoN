import wx, os, sys, wx.lib.scrolledpanel

sys.path.insert(0, os.path.expanduser("/home/labb/ENVISIoN-appDev/envision/envision/GUI"))

from VisFrame import VisualizationFrame
from ParserPane import ParserPane    
from generalFrame import GeneralFrame


class Coll_Panel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.visFrame = VisualizationFrame(self,
                                           label="Visualization")
        self.parseFrame = ParserPane(self,label="Parser")
        
        
        # Maybe use non specific frames and build gui from that
        
        # Top level collapsible
        topFrame = GeneralFrame(self, label="Top level menu")

        # Sub collapsible
        subFrame = GeneralFrame(topFrame.pane, label="-Level 1 menu")
        subFrame.parent_pane = topFrame
        topFrame.add_sub_item(subFrame)

        # Button under sub menu
        subButton = wx.Button(subFrame.pane, label = str('Level 2 button'))
        subFrame.add_sub_item(subButton, wx.SizerFlags().Expand().Border(wx.ALL, 10))
        
        # Menu under that
        subFrame_2 = GeneralFrame(subFrame.pane, label="--Level 2 menu")
        subFrame_2.parent_pane = subFrame
        subFrame.add_sub_item(subFrame_2)

        # Button under menu
        subButton_2 = wx.Button(subFrame_2.pane, label = str('Level 2 button'))
        subFrame_2.add_sub_item(subButton_2, wx.SizerFlags().Expand().Border(wx.ALL, 10))

        # Button under top menu
        topButton = wx.Button(topFrame.pane, label = str('Level 1 button'))
        topFrame.add_sub_item(topButton)

        # Add the top frame to this window
        sizer.Add(topFrame,0)

        
        sizer.Add(self.parseFrame,0)
        sizer.Add(self.visFrame,0)
        self.SetSizer(sizer)




class Main_Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.coll_panel =Coll_Panel(self.main_panel,-1, pos=(-1,-1),
                                    size=(-1,300))
        self.coll_panel.SetupScrolling(scroll_y=True)
        sizer.Add(self.coll_panel,2, wx.EXPAND )
        self.main_panel.SetSizer(sizer)
        
    
        
class ENVISIoN(wx.App):
    def OnInit(self):
        frame = Main_Frame(None, title = "ENVISIoN")
        frame.SetSize(0,0,300,600)
        bg_colour = wx.Colour(76,75,77)
        frame.SetBackgroundColour(bg_colour)
        frame.Show(True)
        frame.Centre()
        return True

def main():
    app = ENVISIoN(0)
    app.MainLoop()

main()

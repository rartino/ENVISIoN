import wx, os, sys, wx.lib.scrolledpanel

sys.path.insert(0, os.path.expanduser("C:\ENVISIoN\GUI"))

from VisFrame import VisualizationFrame
from ParserPane import ParserPane    


class Coll_Panel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, *args, **kwargs):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.visFrame = VisualizationFrame(self,
                                           label="Visualization")
        self.parseFrame = ParserPane(self,label="Parser")
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

if __name__ == "__main__":
    main()

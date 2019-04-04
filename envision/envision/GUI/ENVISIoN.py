import wx, os, sys, wx.lib.scrolledpanel

sys.path.insert(0, os.path.expanduser("/C:/ENVISIoN/envision/envision/GUI"))

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
        self.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)




class Main_Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.coll_panel =Coll_Panel(self.main_panel,-1)
        
        
        sizer.Add(self.coll_panel,2, wx.EXPAND )
        self.main_panel.SetSizer(sizer)
        self.coll_panel.parseFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.parse_change)
        self.coll_panel.visFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.vis_change)
        self.coll_panel.visFrame.PKFFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.PKF_change) 
        self.coll_panel.visFrame.chargeFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,
                         self.charge_change)
        self.coll_panel.visFrame.dosFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.dos_change)
        self.coll_panel.visFrame.parchgFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,
                         self.parchg_change)
        self.coll_panel.visFrame.unitcellFrame.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED,
                         self.unitcell_change)
        
    def parse_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)

    def vis_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.on_change(event)

    def PKF_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.PKF_change(event)

    def charge_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.charge_change(event)
    
    def dos_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.dos_change(event)

    def parchg_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.parchg_change(event)

    def unitcell_change(self, event):
        self.coll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)
        self.coll_panel.visFrame.unitcell_change(event)

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

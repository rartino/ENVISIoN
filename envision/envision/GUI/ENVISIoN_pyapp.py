#
#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import wx, os, sys, wx.lib.scrolledpanel
import inspect
path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir))
from VisFrame import VisualizationFrame
from ParserPane import ParserPane 
from generalCollapsible import GeneralCollapsible


class Main_Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        self.main_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
    
    #Scrollable panel
        scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_panel =wx.lib.scrolledpanel.ScrolledPanel(self.main_panel,-1)
        sizer.Add(self.scroll_panel,2, wx.EXPAND)
        self.parseFrame = ParserPane(self.scroll_panel)
        scrollSizer.Add(self.parseFrame,0)
        self.visFrame = VisualizationFrame(self.scroll_panel)
        scrollSizer.Add(self.visFrame,0)
        self.scroll_panel.SetSizer(scrollSizer)
        self.scroll_panel.SetupScrolling(scroll_x=False, 
                                        scroll_y=True, rate_x=20, 
                                        rate_y=20, scrollToTop=True, 
                                        scrollIntoView=False)

        self.main_panel.SetSizer(sizer)
        

class ENVISIoN(wx.App):
    def OnInit(self):
        self.frame = Main_Frame(None, title = "ENVISIoN")
        self.frame.SetSize(0,0,400,600)
        bg_colour = wx.Colour(208,206,206)
        self.frame.SetBackgroundColour(bg_colour)
        self.frame.Show(True)
        self.frame.Centre()
        return True

    def on_timer(self):
        self.inviwoApp.update()
        wx.CallLater(1000/60, self.on_timer)

def main(inviwoApp):
    app = ENVISIoN(0)
    app.inviwoApp = inviwoApp
    app.on_timer()

    app.frame.visFrame.set_inviwo_app(inviwoApp)
    app.MainLoop()



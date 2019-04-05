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
"""The main file for the GUI of ENVISIoN. The app, main frame and main panel is """
"""defined here.                                                                """
"""*****************************************************************************"""

import wx, os, sys, wx.lib.scrolledpanel
sys.path.insert(0, os.path.expanduser(os.getcwd()))

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
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
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

    def OnCloseWindow(self, event):
        self.coll_panel.parseFrame.messageFrame.Destroy()
        self.coll_panel.parseFrame.dirFrame.Destroy()
        self.coll_panel.parseFrame.Destroy()
        self.coll_panel.visFrame.Destroy()
        self.coll_panel.Destroy()
        self.Destroy()
        

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


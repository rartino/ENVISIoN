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
"""The main file for the GUI of ENVISIoN. The app, main frame and main panel is """
"""defined here.                                                                """
"""*****************************************************************************"""

import wx, os, sys, wx.lib.scrolledpanel
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))
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
        self.frame.SetSize(0,0,300,600)
        bg_colour = wx.Colour(208,206,206)
        self.frame.SetBackgroundColour(bg_colour)
        self.frame.Show(True)
        self.frame.Centre()
        return True

def main():
    app = ENVISIoN(0)
    app.MainLoop()

main()


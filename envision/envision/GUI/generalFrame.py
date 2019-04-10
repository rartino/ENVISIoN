import wx, sys, os

class GeneralFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        #init and add all elements in visFrame
        self.parent_pane = None
        self.pane = self.GetPane()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.pane.SetSizer(self.sizer)
        
        self.bg_colour = wx.Colour(255,255,255)
        self.SetBackgroundColour(self.bg_colour)
    

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_change)


    def add_sub_item(self, item, sizer_flags = wx.SizerFlags()):
        self.sizer.Add(item, sizer_flags)

    def on_change(self, event = None):
        print("Menu collapse changed")

        # For some reason this makes the sub panels expand correctly
        # Some dark powers are probobly involved
        if self.parent_pane != None:
            print("Flipping pane")
            self.parent_pane.Layout()
            self.parent_pane.Collapse(not self.parent_pane.IsCollapsed())
            self.parent_pane.Collapse(not self.parent_pane.IsCollapsed())
            self.parent_pane.Layout()
            self.parent_pane.on_change()

        # Update the layout of parent widgets
        self.Layout()
        widget = self
        while True:
         widget = widget.GetParent()
         widget.Layout()
         if widget.IsTopLevel():
             break

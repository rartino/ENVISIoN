import wx, sys, os

class GeneralCollapsible(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        wx.CollapsiblePane.__init__(self, *args,**kwargs)

        self.parent_collapsible = None
        self.pane = self.GetPane()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.pane.SetSizer(self.sizer)
        
        self.bg_colour = wx.Colour(255,255,255)
        self.SetBackgroundColour(self.bg_colour)
    
        # Default callback when collapsing panel, just updates the layouts to make sizers expand
        # Can freely be changed in subclasses, just make sure to call update_layout there aswell
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.update_layout)

        self.sub_collapsibles = []

    def add_item(self, item, sizer_flags = wx.SizerFlags()):
        # Add some wx widged to the expandible panel
        self.sizer.Add(item, sizer_flags)

    def add_sub_collapsible(self, item):
        # Add a collapsible panel
        self.sizer.Add(item)
        self.sub_collapsibles.append(item)
        item.parent_collapsible = self

    def set_callback(self, func):
        # Sets a callback to trigger on collapse event
        # and updates the layout after running callback
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, 
            lambda event : (
                func(self),
                self.update_layout()))

    
    def collapse_children(self):
        for collapsible in self.sub_collapsibles:
            collapsible.collapse_children()
        self.Collapse(True)

    def update_layout(self, event = None):
        # Updates the layout of the collapsible
        # Fixes the size of things look correct after collapse

        # If collapsed collapse all sub collapsibles
        if self.IsCollapsed():
            self.collapse_children()
            
        # For some reason this makes the sub panels expand correctly
        # Seems to be needed on linux, can maybe be simplified tho.
        if self.parent_collapsible != None:
            self.parent_collapsible.Collapse(not self.parent_collapsible.IsCollapsed())
            self.parent_collapsible.Collapse(not self.parent_collapsible.IsCollapsed())
            self.parent_collapsible.Layout()
            self.parent_collapsible.update_layout()

        # Update the layout of parent widgets
        self.Layout()
        widget = self
        while True:
         widget = widget.GetParent()
         widget.Layout()
         if widget.IsTopLevel():
             break

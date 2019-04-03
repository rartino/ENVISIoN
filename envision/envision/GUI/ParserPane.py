import wx

class ParserPane(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.bg_colour = wx.Colour(76,75,77)
        self.SetBackgroundColour(self.bg_colour)
        sizer.Add(wx.Button(self.GetPane(), label = str('...')),wx.GROW,1)
        sizer.Add(wx.Button(self.GetPane(), label = str('Parse')),wx.GROW,1)
        sizer.Add(wx.Button(self.GetPane(), label = str('Parse')),wx.GROW,1)
        sizer.Add(wx.Button(self.GetPane(), label = str('Parse')),wx.GROW,1)
        sizer.Add(wx.Button(self.GetPane(), label = str('Parse')),wx.GROW,1)
        sizer.Add(wx.Button(self.GetPane(), label = str('Parse')),wx.GROW,1)
        
        self.GetPane().SetSizer(sizer)

    def on_change(self, event):
        self.GetParent().Layout()
        if self.IsCollapsed():
            print('HEJDÅ')
        else:
            print('HEJ')

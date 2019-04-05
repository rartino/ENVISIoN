import wx,sys,os

class UnitcellFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        unitcellPane = self.GetPane()
        unitcellSizer = wx.BoxSizer(wx.VERTICAL)
        unitcellPane.SetSizer(unitcellSizer)
        
                
        button1 = wx.Button(unitcellPane, label="X")
        button2 = wx.Button(unitcellPane, label="Y")
        
        slider = wx.Slider(unitcellPane)
        unitcellSizer.Add(button1,wx.GROW, 0)
        unitcellSizer.Add(button2,wx.GROW, 0)
        unitcellSizer.Add(slider,wx.GROW, 0)

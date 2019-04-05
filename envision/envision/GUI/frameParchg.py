import wx,sys,os

class ParchgFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        parchgPane = self.GetPane()
        parchgSizer = wx.BoxSizer(wx.VERTICAL)
        parchgPane.SetSizer(parchgSizer)
        
                
        button1 = wx.Button(parchgPane, label="X")
        button2 = wx.Button(parchgPane, label="Y")
        slider = wx.Slider(parchgPane)
        parchgSizer.Add(button1,wx.GROW, 0)
        parchgSizer.Add(button2,wx.GROW, 0)
        parchgSizer.Add(slider,wx.GROW, 0)

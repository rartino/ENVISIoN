import wx,sys,os

class PKFFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        PKFPane = self.GetPane()
        PKFSizer = wx.BoxSizer(wx.VERTICAL)
        PKFPane.SetSizer(PKFSizer)
        
                
        button1 = wx.Button(PKFPane, label="X")
        button2 = wx.Button(PKFPane, label="Y")
        slider = wx.Slider(PKFPane)
        PKFSizer.Add(button1,wx.GROW, 1)
        PKFSizer.Add(button2,wx.GROW, 1)
        PKFSizer.Add(slider,wx.GROW, 1)

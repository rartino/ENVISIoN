import wx,sys,os

class DosFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        dosPane = self.GetPane()
        dosSizer = wx.BoxSizer(wx.VERTICAL)
        dosPane.SetSizer(dosSizer)
        
                
        button1 = wx.Button(dosPane, label="X")
        button2 = wx.Button(dosPane, label="Y")
        slider = wx.Slider(dosPane)
        dosSizer.Add(button1,wx.GROW, 0)
        dosSizer.Add(button2,wx.GROW, 0)
        dosSizer.Add(slider,wx.GROW, 0)

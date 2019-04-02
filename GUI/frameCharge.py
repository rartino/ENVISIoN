import wx,sys,os

class ChargeFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        chargePane = self.GetPane()
        chargeSizer = wx.BoxSizer(wx.VERTICAL)
        chargePane.SetSizer(chargeSizer)
        
        chargeSizer.Add(wx.Button(chargePane, label = str('X')),
                     wx.GROW | wx.ALL, 2)
        chargeSizer.Add(wx.Button(chargePane, label = str('Y')),
                     wx.GROW | wx.ALL, 2)
        chargePane.SetSizer(chargeSizer)

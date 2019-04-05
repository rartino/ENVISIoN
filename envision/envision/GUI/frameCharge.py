import wx,sys,os
from parameter_utils import *
from VisFrame import *
class ChargeFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        chargePane = self.GetPane()
        chargeSizer = wx.BoxSizer(wx.VERTICAL)
        chargePane.SetSizer(chargeSizer)
        self.clearButton=wx.Button(chargePane, label = str('Clear'))
        chargeSizer.Add(self.clearButton,
                     wx.GROW | wx.ALL, 0)
        chargeSizer.Add(wx.Button(chargePane, label = str('Y')),
                     wx.GROW | wx.ALL, 0)
        chargePane.SetSizer(chargeSizer)

        self.clearButton.Bind(wx.EVT_BUTTON, self.clear_pressed)

    def clear_pressed(self,event):
        charge_clear_tf()
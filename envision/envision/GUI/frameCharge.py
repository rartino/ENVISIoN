import wx,sys,os
from parameter_utils import *
from VisFrame import *
class ChargeFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        
        chargePane = self.GetPane()
        chargeSizer = wx.BoxSizer(wx.VERTICAL)
        chargePane.SetSizer(chargeSizer)
        self.button1=wx.Button(chargePane, label = str('X'))
        chargeSizer.Add(self.button1,
                     wx.GROW | wx.ALL, 0)
        chargeSizer.Add(wx.Button(chargePane, label = str('Y')),
                     wx.GROW | wx.ALL, 0)
        chargePane.SetSizer(chargeSizer)

        self.button1.Bind(wx.EVT_BUTTON, self.button_pressed_X)

    def button_pressed_X(self,event):
        charge_clear_tf()
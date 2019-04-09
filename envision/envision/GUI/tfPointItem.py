import wx

class TFPointWidget(wx.BoxSizer):
    def __init__(self, parent, value, alpha, colour):
        super().__init__(wx.HORIZONTAL)

        self.value = float(value)
        self.alpha = float(alpha)
        self.colour = colour

        self.valueText = wx.TextCtrl(parent, value=str(value))
        self.alphaText = wx.TextCtrl(parent, value=str(alpha))
        self.delButton = wx.Button(parent, label = '-', size = wx.Size(23, 23))

        self.Add(self.valueText)
        self.Add(self.alphaText)
        self.Add(self.delButton)





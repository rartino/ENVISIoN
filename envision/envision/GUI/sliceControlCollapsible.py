
import wx
from generalCollapsible import GeneralCollapsible

# TODO: Integrate with inviwo
# TODO: height slider does not work with custom normal

class SliceControlCollapsible(GeneralCollapsible):
    def __init__(self, parent, label):
        super().__init__(parent, label = label)
        
        pane = self.GetPane()

        # Plane normal controls
        normalLabel = wx.StaticText(pane, label="Slice plane normal:")
        normalLabel.SetToolTip(
            "Set the normal vector of slice plane\n" + 
            "Input X, Y, and Z component in text fields.")
        self.add_item(normalLabel)

        self.xInput = wx.TextCtrl(pane, value="0", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))
        self.yInput = wx.TextCtrl(pane, value="1", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))
        self.zInput = wx.TextCtrl(pane, value="0", style=wx.TE_PROCESS_ENTER, size=wx.Size(40, 23))

        normalHBox = wx.BoxSizer(wx.HORIZONTAL)
        normalHBox.Add(self.xInput)
        normalHBox.Add(self.yInput)
        normalHBox.Add(self.zInput)
        self.add_item(normalHBox)

        # Events to read input on
        self.xInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.xInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)
        self.yInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.yInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)
        self.zInput.Bind(wx.EVT_KILL_FOCUS, self.normal_input_changed)
        self.zInput.Bind(wx.EVT_TEXT_ENTER, self.normal_input_changed)

        sliderLabel = wx.StaticText(pane, label="Slice plane height:")
        sliderLabel.SetToolTip(
            "Use the slider to select height of slice plane\n" + 
            "0% - Bottom of the volume\n" + 
            "100% - Top of the volume")
        self.add_item(sliderLabel)

        # Plane mover slider
        self.heightSlider = wx.Slider(pane, minValue=0, maxValue=100, value=50)
        self.heightSlider.Bind(wx.EVT_SCROLL, self.slider_changed)

        self.add_item(self.heightSlider)

    def normal_input_changed(self, event):
        try:
            x = float(self.xInput.GetLineText(0))
            y = float(self.yInput.GetLineText(0))
            z = float(self.zInput.GetLineText(0))
        except:
            raise ValueError("Input values must be valid float values")

        if x == y == z == 0:
            raise ValueError("Normal must be separated from 0")

        
        print(str(x) + ":" + str(y) + ":" + str(z))

    def slider_changed(self, event):
        print(self.heightSlider.GetValue())





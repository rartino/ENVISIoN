import wx, sys, os

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision/envision/GUI"))
from frameCharge import ChargeFrame
from framePKF import PKFFrame
from frameDoS import DosFrame
from frameParchg import ParchgFrame
from frameUnitcell import UnitcellFrame

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision"))
import envision
import envision.inviwo
import parameter_utils
PATH_TO_HDF5=os.path.expanduser("C:/Users/sille/Downloads/demo_charge.hdf5")

class VisualizationFrame(wx.CollapsiblePane):
    def __init__(self, *args, **kwargs,):
        wx.CollapsiblePane.__init__(self,*args,**kwargs)
        #init and add all elements in visFrame
        visSizer = wx.BoxSizer(wx.VERTICAL)
        visPane = self.GetPane()
        self.PKFFrame = PKFFrame(visPane,label="PKF")
        self.chargeFrame = ChargeFrame(visPane,label="Charge")
        self.dosFrame = DosFrame(visPane,label="Density Of State")
        self.parchgFrame = ParchgFrame(visPane,label="Charge")
        self.unitcellFrame = UnitcellFrame(visPane,label="Unitcell")

        
        visSizer.Add(self.chargeFrame,0)
        visSizer.Add(self.PKFFrame,0)
        visSizer.Add(self.dosFrame,0)
        visSizer.Add(self.parchgFrame,0)
        visSizer.Add(self.unitcellFrame,0)
        
        self.bg_colour = wx.Colour(76,75,77)
        self.SetBackgroundColour(self.bg_colour)
        self.PKFFrame.SetBackgroundColour(self.bg_colour)
        self.chargeFrame.SetBackgroundColour(self.bg_colour)
        self.dosFrame.SetBackgroundColour(self.bg_colour)
        self.parchgFrame.SetBackgroundColour(self.bg_colour)
        self.unitcellFrame.SetBackgroundColour(self.bg_colour)

        self.dosCollapsed = True
        self.parchgCollapsed = True
        self.unitcellCollapsed = True
        self.chargeCollapsed = True
        self.PKFCollapsed = True
        self.collapsed = True
    
        visPane.SetSizer(visSizer)


    def on_change(self, event):
        self.GetParent().Layout()
        if self.collapsed:
            #when Vis-frame is collapsed, collapse all subframes
            self.chargeFrame.Collapse(True)
            self.PKFFrame.Collapse(True)
            self.dosFrame.Collapse(True)
            self.parchgFrame.Collapse(True)
            self.unitcellFrame.Collapse(True)
            self.collapsed = False
            self.chargeCollapsed = True
            self.PKFCollapsed = True
            self.dosCollapsed = False
            self.parchgCollapsed = True
            self.unitcellCollapsed = True
        elif not self.collapsed:
            self.collapsed = True
            print('HEJ')

    def PKF_change(self, event):
        if not self.collapsed:
            self.Collapse(True)
            self.Collapse(False)
        if self.PKFCollapsed:
            #PKF-function
            print('PKF')
            self.PKFCollapsed = False
        else:
            print('notPKF')
            self.PKFCollapsed = True

    def charge_change(self, event):
        if not self.collapsed:
            self.Collapse(True)
            self.Collapse(False)
        if self.chargeCollapsed:
            envision.inviwo.charge(PATH_TO_HDF5, iso = None,
                               slice = False, xpos = 0, ypos = 0)
            print('Charge')
            self.chargeCollapsed = False
        else:
            print('notCharge')
            self.chargeCollapsed = True

    def dos_change(self, event):
        if not self.collapsed:
            self.Collapse(True)
            self.Collapse(False)
        if self.dosCollapsed:
            #DoS-function
            print('DoS')
            self.dosCollapsed = False
        else:
            print('notDoS')
            self.dosCollapsed = True

    def parchg_change(self, event):
        if not self.collapsed:
            self.Collapse(True)
            self.Collapse(False)
        if self.parchgCollapsed:
            #parchg-function
            print('parchg')
            self.parchgCollapsed = False
        else:
            print('notparchg')
            self.parchgCollapsed = True

    def unitcell_change(self, event):
        if not self.collapsed:
            self.Collapse(True)
            self.Collapse(False)
        if self.unitcellCollapsed:
            #unitcell-function
            print('unitcell')
            self.unitcellCollapsed = False
        else:
            print('notunitcell')
            self.unitcellCollapsed = True

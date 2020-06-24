import inviwopy
import numpy as np
import h5py
import inviwopy.glm as glm
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork

# TODO add volume merger and multi-raycaster

class SliceSubnetwork(Subnetwork):
    '''
    Manages a subnetwork for volume slice rendering. 
    Used for charge and ELF visualisations.

    _Inports_
        volumeInports, Volume.inport. Volumes should have the same dimensions.
    _Outports_
        imageOutport, Image.outport slice rendering image.
    '''
    def __init__(self, inviwoApp):
        Subnetwork.__init__(self, inviwoApp)
        self.setup_network(-6, 3)


# ------------------------------------------
# ------- Network building functions -------

    # def connect_image(self, image_outport):
    #     inport = self.get_processor('Mesh Renderer').getInport('imageInport')
    #     self.network.addConnection(image_outport, inport)

    def connect_volume(self, volume_outport):
        inport = self.get_processor('Volume Slice').getInport('inport')
        self.network.addConnection(volume_outport, inport)


    def link_camera(self, cameraProp):
        pass

    def link_plane(self, raycaster):
        volumeSlice = self.get_processor('Volume Slice').getInport('inport')
        self.network.addLink(volumeSlice.planePosition, raycaster.positionindicator.plane1.position)
        self.network.addLink(volumeSlice.planeNormal, raycaster.positionindicator.plane1.normal)
        raycaster.positionindicator.plane1.enable.value = True
        raycaster.positionindicator.plane2.enable.value = False
        raycaster.positionindicator.plane3.enable.value = False
        raycaster.positionindicator.plane1.color.value = inviwopy.glm.vec4(1, 1, 1, 0.3)

    def setup_network(self, ypos, xpos):

        # # Setup slice rendering
        volumeSlice = self.add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xpos, ypos+3)   
        sliceBackground = self.add_processor('org.inviwo.Background', 'SliceBackground', xpos, ypos+6)
        sliceCanvas = self.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos, ypos+9)
        sliceCanvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)       
        # SliceCanvas.widget.show()

        # # self.network.addConnection(HDFvolume.getOutport('outport'), VolumeSlice.getInport('volume'))
        self.network.addConnection(volumeSlice.getOutport('outport'), sliceBackground.getInport('inport'))
        self.network.addConnection(sliceBackground.getOutport('outport'), sliceCanvas.getInport('inport'))



        # entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
        # entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)

        # # Setup slice plane
        # pos_indicator = Raycaster.positionindicator
        # pos_indicator.plane1.enable.value = True
        # pos_indicator.plane2.enable.value = False
        # pos_indicator.plane3.enable.value = False
        # pos_indicator.enable.value = False # Disabled by default
        # pos_indicator.plane1.color.value = inviwopy.glm.vec4(1, 1, 1, 0.5)

        # # Connect unitcell and volume visualisation.
        # try:
        #     UnitCellRenderer = self.get_processor('Unit Cell Renderer')
        # except ProcessorNotFoundError:
        #     print("No unitcell processor active")
        # else:
        #     self.network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
        #     self.network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
        #     self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))

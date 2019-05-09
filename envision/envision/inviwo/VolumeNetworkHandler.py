

import sys,os,inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py
from common import _add_h5source, _add_processor

class VolumeNetworkHandler():
    """ Base class for setting up and handling a network for generic volume rendering for ENVISIoN.
    Need to be supplied with outports of volume data from somewhere.
    Not used directly, is inherited in other classes for handling specific visualizations


    """
    def __init__(self):

        self.volumeInports = []
        self.setup_volume_network()
        pass


# ------------------------------------------
# ------- Property control functions -------






# ------------------------------------------
# ------- Network building functions -------

    def toggle_slice_canvas(self, enable_slice):
    # Will add or remove the slice canvas
        network = inviwopy.app.network

        SliceCanvas = network.getProcessorByIdentifier('SliceCanvas')

        # If already in correct mode dont do anything
        if (SliceCanvas and enable_slice) or (not SliceCanvas and not enable_slice):
            return

        if enable_slice:
            SliceCanvas = _add_processor('org.inviwo.CanvasGL', 'SliceCanvas', 25*7, 525)
            network.addConnection(network.getProcessorByIdentifier('SliceBackground').getOutport('outport'), SliceCanvas.getInport('inport'))
        else:
            network.removeProcessor(SliceCanvas)

    def connect_volume(self, volume_outport):
        network = inviwopy.app.network
        for inport in self.volumeInports:
            network.addConnection(volume_outport, inport)

    def setup_volume_network(self):
    # Setup the generic part of volume rendering network.
        xpos = 0
        ypos = 0

        network = inviwopy.app.network

        # Add "Bounding Box" and "Mesh Renderer" processors to visualise the borders of the volume
        BoundingBox = _add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xpos+200, ypos+150)    
        MeshRenderer = _add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xpos+200, ypos+225)

        # Add processor to pick which part of the volume to render
        CubeProxyGeometry = _add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xpos+30, ypos+150)
        
        # Add processor to control the camera during the visualisation
        EntryExitPoints = _add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xpos+30, ypos+225)

        Raycaster = _add_processor('org.inviwo.VolumeRaycaster', "Raycaster", xpos, ypos+300)

        # Setup Slice rendering part
        VolumeSlice = _add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xpos-25*7, ypos+300)          
        SliceCanvas = _add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos-25*7, ypos+525)
        SliceBackground = _add_processor('org.inviwo.Background', 'SliceBackground', xpos-25*7, ypos+450)
        
        # network.addConnection(HDFvolume.getOutport('outport'), VolumeSlice.getInport('volume'))
        network.addConnection(VolumeSlice.getOutport('outport'), SliceBackground.getInport('inport'))
        network.addConnection(SliceBackground.getOutport('outport'), SliceCanvas.getInport('inport'))

        # Setup volume rendering part
        Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xpos, ypos+525)
        VolumeBackground = _add_processor('org.inviwo.Background', 'VolumeBackground', xpos, ypos+450)
        
        network.addConnection(Raycaster.getOutport('outport'), VolumeBackground.getInport('inport'))
        network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))

        network.addLink(VolumeSlice.getPropertyByIdentifier('planePosition'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.position)
        network.addLink(VolumeSlice.getPropertyByIdentifier('planeNormal'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.normal)

        # Shared connections and properties between electron density and electron localisation function data
        network.addConnection(MeshRenderer.getOutport('image'), Raycaster.getInport('bg'))
        network.addConnection(EntryExitPoints.getOutport('entry'), Raycaster.getInport('entry'))
        network.addConnection(EntryExitPoints.getOutport('exit'), Raycaster.getInport('exit'))
        # network.addConnection(HDFsource.getOutport('outport'), HDFvolume.getInport('inport'))
        # network.addConnection(HDFvolume.getOutport('outport'), BoundingBox.getInport('volume'))
        # network.addConnection(HDFvolume.getOutport('outport'), CubeProxyGeometry.getInport('volume'))
        # network.addConnection(HDFvolume.getOutport('outport'), Raycaster.getInport('volume'))
        network.addConnection(BoundingBox.getOutport('mesh'), MeshRenderer.getInport('geometry'))
        network.addConnection(CubeProxyGeometry.getOutport('proxyGeometry'), EntryExitPoints.getInport('geometry'))
        network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))
        network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), EntryExitPoints.getPropertyByIdentifier('camera'))

        self.volumeInports.append(BoundingBox.getInport('volume'))
        self.volumeInports.append(CubeProxyGeometry.getInport('volume'))
        self.volumeInports.append(Raycaster.getInport('volume'))
        self.volumeInports.append(VolumeSlice.getInport('volume'))

        entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
        entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)

        # Connect unit cell and volume visualisation.
        UnitCellRenderer = network.getProcessorByIdentifier('Unit Cell Renderer')
        if UnitCellRenderer:
            network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
            network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
            network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))

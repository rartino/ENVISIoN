import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork

# TODO add volume merger and multi-raycaster

class VolumeSubnetwork(Subnetwork):
    '''
    Manages a subnetwork for generic volume rendering. 
    Used for charge and ELF visualisations.

    _Inports_
        volumeInports, 4x Volume.inport. Volumes should have the same dimensions.
        imageInport, 1 Image.inport. If image should have a depth layer and the same camera angle to be rendered inside the volume.
    _Outports_
        imageOutport, Image.outport volume rendering with image rendered inside.
    '''
    def __init__(self, inviwoApp, xpos=0, ypos=0):
        Subnetwork.__init__(self, inviwoApp)
        self.setup_network(xpos, ypos)


# ------------------------------------------
# ------- Network building functions -------

    def link_camera(self, camera_prop):
        meshRenderer = self.get_processor('Mesh Renderer')
        self.network.addLink(meshRenderer.camera, camera_prop)

    def connect_decoration(self, image_outport):
        inport = self.get_processor('Mesh Renderer').getInport('imageInport')
        self.network.addConnection(image_outport, inport)

    def connect_hdf5(self, handle_outport):
        inport = self.get_processor('HDF5 path').getInport('inport')
        self.network.addConnection(handle_outport, inport)

    def set_hdf5_subpath(self, path):
        hdf5Path = self.get_processor('HDF5 path')
        hdf5Path.selection.selectedValue = path

    def setup_network(self, xpos, ypos):
        # Setup volume data source
        # Generic hdf5 to volume
        hdf5Path = self.add_processor('org.inviwo.hdf5.PathSelection', 'HDF5 path', xpos, ypos)
        hdf5Volume = self.add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 selection', xpos, ypos+3)

        # Bounding box around volume
        boundingBox = self.add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xpos+8, ypos+6)    
        meshRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xpos+8, ypos+9)
        
        # Setup volume racaster
        cubeProxy = self.add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xpos+1, ypos+6)
        entryExit = self.add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xpos+1, ypos+9)
        raycaster = self.add_processor('org.inviwo.VolumeRaycaster', "Raycaster", xpos, ypos+12)
        
        # Volume canvas
        volumeBackground = self.add_processor('org.inviwo.Background', 'VolumeBackground', xpos, ypos+15)
        volumeCanvas = self.add_processor('org.inviwo.CanvasGL', 'VolumeCanvas', xpos, ypos+18)

        # Setup slice rendering
        volumeSlice = self.add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xpos-7, ypos+12)   
        sliceBackground = self.add_processor('org.inviwo.Background', 'SliceBackground', xpos-7, ypos+15)
        sliceCanvas = self.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos-7, ypos+18)
        sliceCanvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)       
        
        # Connect processors
        self.network.addConnection(hdf5Path.getOutport('outport'), hdf5Volume.getInport('inport'))

        self.network.addConnection(hdf5Volume.getOutport('outport'), boundingBox.getInport('volume'))
        self.network.addConnection(hdf5Volume.getOutport('outport'), cubeProxy.getInport('volume'))
        self.network.addConnection(hdf5Volume.getOutport('outport'), raycaster.getInport('volume'))

        self.network.addConnection(cubeProxy.getOutport('proxyGeometry'), entryExit.getInport('geometry'))
        self.network.addConnection(entryExit.getOutport('entry'), raycaster.getInport('entry'))
        self.network.addConnection(entryExit.getOutport('exit'), raycaster.getInport('exit'))

        self.network.addConnection(boundingBox.getOutport('mesh'), meshRenderer.getInport('geometry'))
        self.network.addConnection(meshRenderer.getOutport('image'), raycaster.getInport('bg'))

        self.network.addConnection(raycaster.getOutport('outport'), volumeBackground.getInport('inport'))
        self.network.addConnection(volumeBackground.getOutport('outport'), volumeCanvas.getInport('inport'))
        
        self.network.addConnection(hdf5Volume.getOutport('outport'), volumeSlice.getInport('volume'))
        self.network.addConnection(volumeSlice.getOutport('outport'), sliceBackground.getInport('inport'))
        self.network.addConnection(sliceBackground.getOutport('outport'), sliceCanvas.getInport('inport'))

        # Link properties
        self.network.addLink(meshRenderer.camera, entryExit.camera)
        self.network.addLink(volumeSlice.planePosition, raycaster.positionindicator.plane1.position)
        self.network.addLink(volumeSlice.planeNormal, raycaster.positionindicator.plane1.normal)

        # Set default properties
        raycaster.raycaster.samplingRate.value = 4
        raycaster.positionindicator.plane1.enable.value = True
        raycaster.positionindicator.plane2.enable.value = False
        raycaster.positionindicator.plane3.enable.value = False
        raycaster.positionindicator.plane1.color.value = inviwopy.glm.vec4(1, 1, 1, 0.4)
        raycaster.positionindicator.enable.value = False
        sliceCanvas.widget.hide()

        self.image_outport = raycaster.getOutport('outport')

        # entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
        # entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)

        # # Connect unitcell and volume visualisation.
        # try:
        #     UnitCellRenderer = self.get_processor('Unit Cell Renderer')
        # except ProcessorNotFoundError:
        #     print("No unitcell processor active")
        # else:
        #     self.network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
        #     self.network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
        #     self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))

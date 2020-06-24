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
    def __init__(self, inviwoApp):
        Subnetwork.__init__(self, inviwoApp)
        self.setup_network(0, 3)


# ------------------------------------------
# ------- Network building functions -------

    # def connect_image(self, image_outport):
    #     inport = self.get_processor('Mesh Renderer').getInport('imageInport')
    #     self.network.addConnection(image_outport, inport)

    def connect_hdf5(self, handle_outport):
        inport = self.get_processor('HDF5 path').getInport('inport')
        self.network.addConnection(handle_outport, inport)


    def set_hdf5_subpath(self, path):
        hdf5Path = self.get_processor('HDF5 path')
        hdf5Path.selection.selectedValue = path

    def setup_network(self, ypos, xpos):
        # Setup volume data source
        # Generic hdf5 to volume
        hdf5Path = self.add_processor('org.inviwo.hdf5.PathSelection', 'HDF5 path', 0, ypos)
        hdf5Volume = self.add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 selection', 0, ypos+3)

        # Bounding box around volume
        boundingBox = self.add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xpos+8, ypos+6)    
        meshRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xpos+8, ypos+9)
        
        # Setup volume racaster
        cubeProxy = self.add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xpos+1, ypos+6)
        entryExit = self.add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xpos+1, ypos+9)

        raycaster = self.add_processor('org.inviwo.VolumeRaycaster', "Raycaster", xpos, ypos+12)
        raycaster.raycaster.samplingRate.value = 4

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

        self.image_outport = raycaster.getOutport('outport')
        print(self.image_outport)


        # # Setup slice rendering
        # VolumeSlice = networkManager.add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xpos-25*7, ypos+300)   
        # SliceCanvas = networkManager.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos-25*7, ypos+525)
        # SliceCanvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)       
        # SliceBackground = networkManager.add_processor('org.inviwo.Background', 'SliceBackground', xpos-25*7, ypos+450)
        # SliceCanvas.widget.show()

        # # self.network.addConnection(HDFvolume.getOutport('outport'), VolumeSlice.getInport('volume'))
        # self.network.addConnection(VolumeSlice.getOutport('outport'), SliceBackground.getInport('inport'))
        # self.network.addConnection(SliceBackground.getOutport('outport'), SliceCanvas.getInport('inport'))

        # # Setup volume rendering part
        # Canvas = self.add_processor('org.inviwo.CanvasGL', 'Canvas', xpos, ypos+525)
        # Canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)
        # VolumeBackground = self.add_processor('org.inviwo.Background', 'VolumeBackground', xpos, ypos+450)
        # Canvas.widget.show()
        
        # self.network.addConnection(Raycaster.getOutport('outport'), VolumeBackground.getInport('inport'))
        # self.network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))

        # self.network.addLink(VolumeSlice.getPropertyByIdentifier('planePosition'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.position)
        # self.network.addLink(VolumeSlice.getPropertyByIdentifier('planeNormal'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.normal)

        # # Shared connections and properties between electron density and electron localisation function data
        # self.network.addConnection(MeshRenderer.getOutport('image'), Raycaster.getInport('bg'))
        # self.network.addConnection(EntryExitPoints.getOutport('entry'), Raycaster.getInport('entry'))
        # self.network.addConnection(EntryExitPoints.getOutport('exit'), Raycaster.getInport('exit'))
        # self.network.addConnection(BoundingBox.getOutport('mesh'), MeshRenderer.getInport('geometry'))
        # self.network.addConnection(CubeProxyGeometry.getOutport('proxyGeometry'), EntryExitPoints.getInport('geometry'))
        # self.network.addConnection(VolumeBackground.getOutport('outport'), Canvas.getInport('inport'))
        # self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), EntryExitPoints.getPropertyByIdentifier('camera'))

        # self.volumeInports.append(BoundingBox.getInport('volume'))
        # self.volumeInports.append(CubeProxyGeometry.getInport('volume'))
        # self.volumeInports.append(Raycaster.getInport('volume'))
        # self.volumeInports.append(VolumeSlice.getInport('volume'))

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

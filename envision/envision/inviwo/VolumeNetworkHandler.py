#
#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################
#
#  Alterations to this file by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys,os,inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
from matplotlib import pyplot as plt 
import h5py
from common import _add_h5source, _add_processor

# TODO: Would probably be better to save important processors as member variables
#       instead of extracting them from the network all the time
#       Low prio: would not really improve anything but code readability

# NOTE: May not be super safe. If someone manually changes the network identifier strings may
#       be invalid, this can cause errors if processors cannot be found. 

class VolumeNetworkHandler():
    """ Base class for setting up and handling a network for generic volume rendering for ENVISIoN.
    Need to be supplied with outports of volume data from somewhere.
    Do not use directly, inherited in other classes for handling specific visualizations.

    """
    def __init__(self):
        self.volumeInports = []
        self.setup_volume_network()

        # Set initial conditions
        self.clear_tf()
        self.toggle_slice_canvas(False)
        self.set_plane_normal()
        self.set_slice_background(inviwopy.glm.vec4(0,0,0,1),
                            inviwopy.glm.vec4(1,1,1,1),3,0)
        self.slice_copy_tf()

    def show_volume_dist(self, path_to_hdf5):
    # Shows a histogram plot over volume data
        network = inviwopy.app.network
        volume = network.getProcessorByIdentifier('HDF5 To Volume')
        with h5py.File(path_to_hdf5,"r") as h5:
            data = h5[volume.volumeSelection.value].value
            result = []
            [ result.extend(el) for el in data[0] ]
            #newResult = []
            #[ newResult.append((element + abs(min(result)))/(max(result) + abs(min(result)))) \
            #    for element in result ]
            print(result)
            dataList= np.array(result)
            plt.hist(dataList,bins=200, density = True)
            plt.title("TF and ISO data") 
            plt.show()

    def clear_processor_network(self):
        network = inviwopy.app.network
        network.clear()



# ------------------------------------------
# ------- Property control functions -------

    def set_mask(self, maskMin, maskMax):
    # Set the mask of the transfer function
    # Only volume densities between maskMin and maskMax are visible after this
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
        if Raycaster:
            Raycaster.isotfComposite.transferFunction.setMask(maskMin, maskMax)
        if VolumeSlice:
            VolumeSlice.tfGroup.transferFunction.setMask(maskMin,maskMax)

    def add_tf_point(self, value, color):
    # Add point to the raycaster transferfunction
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        if Raycaster:
            tf_property = Raycaster.isotfComposite.transferFunction
            tf_property.add(value, color)
            self.slice_copy_tf()

    def slice_copy_tf(self):
    # Function for copying the volume transferfunction to the slice transferfunction
    # Adds a white point just before the first one aswell
        network = inviwopy.app.network
        VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        if VolumeSlice and Raycaster:
            VolumeSlice.tfGroup.transferFunction.value = Raycaster.isotfComposite.transferFunction.value
            #VolumeSlice.tfGroup.transferFunction.add(0.0, inviwopy.glm.vec4(0.0, 0.0, 0.0, 1.0))
            #VolumeSlice.tfGroup.transferFunction.add(1.0, inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))
            tf_points = self.get_tf_points()
            if len(tf_points) > 0:
                VolumeSlice.tfGroup.transferFunction.add(0.99*tf_points[0][0], inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))

    def clear_tf(self):
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        tf_property = Raycaster.isotfComposite.transferFunction
        print(dir(tf_property.mask))
        tf_property.clear()
        self.slice_copy_tf()

    def remove_tf_point(self, index):
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        tf_property = Raycaster.isotfComposite.transferFunction
        if len(self.get_tf_points()) <= index:
            print("No points to remove")
            return
        point_to_remove = tf_property.getValueAt(index)
        tf_property.remove(point_to_remove)
        self.slice_copy_tf()

    def get_tf_points(self):
    # Return a list of all the transferfunction points
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        tf_property = Raycaster.isotfComposite.transferFunction
        return [[x.pos, x.color] for x in tf_property.getValues()]

    def set_shading_mode(self, mode):
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        Raycaster.lighting.shadingMode.value = mode

    def set_volume_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        network = inviwopy.app.network
        Background = network.getProcessorByIdentifier("VolumeBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            Background.bgColor1.value = color_1
        if color_2 != None:
            Background.bgColor2.value = color_2
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def set_slice_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        network = inviwopy.app.network
        Background = network.getProcessorByIdentifier("SliceBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            Background.bgColor1.value = color_1
        if color_2 != None:
            Background.bgColor2.value = color_2
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def toggle_slice_plane(self, enable):
    # Set if the slice plane should be visible in the volume
    # TODO: remove plane.enable.value, move to some initialization code
        network = inviwopy.app.network
        Raycaster = network.getProcessorByIdentifier('Raycaster')
        pos_indicator = Raycaster.positionindicator
        pos_indicator.plane1.enable.value = True
        pos_indicator.plane2.enable.value = False
        pos_indicator.plane3.enable.value = False
        pos_indicator.enable.value = enable

    def set_plane_normal(self, x=0, y=1, z=0):
    # Set the normal of the slice plane
    # x, y, and z can vary between 0 and 1
    # TODO: move sliceAxis.value to some initialization code
        network = inviwopy.app.network
        VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
        VolumeSlice.sliceAxis.value = 3
        VolumeSlice.planeNormal.value = inviwopy.glm.vec3(x, y, z)

    def set_plane_height(self, height):
    # Set the height of the volume slice plane
    # Height can vary between 0 and 1.
        network = inviwopy.app.network
        VolumeSlice = network.getProcessorByIdentifier('Volume Slice')

        # Create position vector based on plane normal 
        normal = VolumeSlice.planeNormal.value
        xHeight = normal.x * height
        yHeight = normal.y * height
        zHeight = normal.z * height
        VolumeSlice.planePosition.value = inviwopy.glm.vec3(xHeight, yHeight, zHeight)

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

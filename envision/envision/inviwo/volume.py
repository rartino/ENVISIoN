#
#  ENVISIoN
#
#  Copyright (c) 2017 David Hartman
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

import inviwopy
import numpy as np
import h5py
from .common import _add_h5source, _add_processor

app = inviwopy.app
network = app.network

# Function for buiding a volume network for both electron density and electron localisation function data (commented out)
def volume_network(h5file, volume, iso, slice, xstart_pos, ystart_pos):
    # Shared processors, processor positions and base vectors between electron density and electron localisation function data
    HDFsource = _add_h5source(h5file, xstart_pos, ystart_pos)
    filenameProperty = HDFsource.getPropertyByIdentifier('filename')
    filenameProperty.value = h5file

    HDFvolume = _add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 To Volume', xstart_pos, ystart_pos+75)
    scaling_factor = 1
    # Read base vectors
    with h5py.File(h5file,"r") as h5:
        basis_4x4=np.identity(4)
        basis_array=np.array(h5["/basis/"], dtype='d')
        basis_4x4[:3,:3]=basis_array
        scaling_factor = h5['/scaling_factor'].value
    BoundingBox = _add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xstart_pos+200, ystart_pos+150)    
    MeshRenderer = _add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xstart_pos+200, ystart_pos+225)
    CubeProxyGeometry = _add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xstart_pos+30, ystart_pos+150)
    EntryExitPoints = _add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xstart_pos+30, ystart_pos+225)
    # Add processor for Volume or ISO Raycaster based on if "iso" is assigned a value or not and give it correct name based on the string "volume" assigned a value in function "charge" or "elf". 
    if iso==None:
        Raycaster = _add_processor('org.inviwo.VolumeRaycaster', volume, xstart_pos, ystart_pos+300)
        raycaster_transferfunction_property = Raycaster.getPropertyByIdentifier('transferFunction')
        raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.6,1.0),inviwopy.glm.vec3(0.0,1.0,1.0))
        raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.45,0.0),inviwopy.glm.vec3(0.0,0.0,1.0))
        raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.7,0.0),inviwopy.glm.vec3(0.0,0.0,0.0))
    else:
        Raycaster = _add_processor('org.inviwo.ISORaycaster', volume, xstart_pos, ystart_pos+300)
        raycaster_isovalue_property = Raycaster.getPropertyByIdentifier('raycasting').getPropertyByIdentifier('isoValue')
        raycaster_isovalue_property.value = iso
        raycaster_surfacecolor_property = Raycaster.getPropertyByIdentifier('surfaceColor')
        raycaster_surfacecolor_property.value = inviwopy.glm.vec4(0.0,0.0,1.0,0.5)
    # Add processors, connections and properties for slice function if slice=True and "iso" hasn't been assigned a value        
    if slice:
        if iso==None:
            VolumeSlice = _add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xstart_pos-170, ystart_pos+300)          
            ImageLayout = _add_processor('org.inviwo.ImageLayoutGL', 'Image Layout', xstart_pos, ystart_pos+375)     
            Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+450)
            Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+525)
            network.addConnection(HDFvolume.getOutport('outport'), VolumeSlice.getInport('volume'))
            network.addConnection(VolumeSlice.getOutport('outport'), ImageLayout.getInport('multiinport'))
            network.addConnection(Raycaster.getOutport('outport'), ImageLayout.getInport('multiinport'))
            network.addConnection(ImageLayout.getOutport('outport'), Background.getInport('inport'))

            ImageLayout.getPropertyByIdentifier('layout').value = 2
            
            network.addLink(VolumeSlice.getPropertyByIdentifier('planePosition'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.position)
            network.addLink(VolumeSlice.getPropertyByIdentifier('planeNormal'), Raycaster.getPropertyByIdentifier('positionindicator').plane1.normal)
            Raycaster_positionindicator_property= Raycaster.getPropertyByIdentifier('positionindicator')
            Raycaster_positionindicator_property.enable = True

            canvas_dimensions_property = Canvas.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimensions')
            canvas_dimensions_property.value = inviwopy.glm.ivec2(700,300)
            volumeSlice_transferfunction_property = VolumeSlice.getPropertyByIdentifier('tfGroup').getPropertyByIdentifier('transferFunction')
            volumeSlice_transferfunction_property.addPoint(inviwopy.glm.vec2(0.0,1.0),inviwopy.glm.vec3(0.0,0.0,1.0))
            volumeSlice_transferfunction_property.addPoint(inviwopy.glm.vec2(0.25,1.0),inviwopy.glm.vec3(0.0,1.0,1.0))
            volumeSlice_transferfunction_property.addPoint(inviwopy.glm.vec2(0.5,1.0),inviwopy.glm.vec3(0.0,1.0,0.0))
            volumeSlice_transferfunction_property.addPoint(inviwopy.glm.vec2(0.75,1.0),inviwopy.glm.vec3(1.0,1.0,0.0))
            volumeSlice_transferfunction_property.addPoint(inviwopy.glm.vec2(1.0,1.0),inviwopy.glm.vec3(1.0,0.0,0.0))

            Raycaster_plane1_property = Raycaster.getPropertyByIdentifier('positionindicator').plane1
            Raycaster_plane2_property = Raycaster.getPropertyByIdentifier('positionindicator').plane2
            Raycaster_plane3_property = Raycaster.getPropertyByIdentifier('positionindicator').plane3
            Raycaster_plane1_property.enable = True
            Raycaster_plane2_property.enable = False
            Raycaster_plane3_property.enable = False

            Raycaster_plane1_color_property = Raycaster_plane1_property.color
            Raycaster_plane1_color_property.value = inviwopy.glm.vec4(1.0,1.0,1.0,0.5)
            
        else:
            print("Slice is not possible with ISO Raycasting, therefore no slice-function is showing.")
    # Add processors, connections and properties for no slice function if slice=False or "iso" has been assigned a value   
    if not slice or iso != None:
        Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+375)
        Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+450)
        network.addConnection(Raycaster.getOutport('outport'), Background.getInport('inport'))
        canvas_dimensions_property = Canvas.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimensions')
        canvas_dimensions_property.value = inviwopy.glm.ivec2(400,400)
        
    # Set correct path to volume data
    if volume=='Charge raycaster':
        hdfvolume_volumeSelection_property = HDFvolume.getPropertyByIdentifier('volumeSelection')
        hdfvolume_volumeSelection_property.value = '/CHG/final' 
    else:
        hdfvolume_volumeSelection_property = HDFvolume.getPropertyByIdentifier('volumeSelection')
        hdfvolume_volumeSelection_property.value = '/ELF/final'
    HDFvolume_basis_property = HDFvolume.getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')
    HDFvolume_basis_property.value = inviwopy.glm.mat4(scaling_factor * basis_4x4[0][0],scaling_factor * basis_4x4[0][1],scaling_factor * basis_4x4[0][2],
                                                       scaling_factor * basis_4x4[0][3],scaling_factor * basis_4x4[1][0],scaling_factor * basis_4x4[1][1],
                                                       scaling_factor * basis_4x4[1][2],scaling_factor * basis_4x4[1][3],scaling_factor * basis_4x4[2][0],
                                                       scaling_factor * basis_4x4[2][1],scaling_factor * basis_4x4[2][2],scaling_factor * basis_4x4[2][3],
                                                       scaling_factor * basis_4x4[3][0],scaling_factor * basis_4x4[3][1],scaling_factor * basis_4x4[3][2],
                                                       scaling_factor * basis_4x4[3][3])
    
    # Shared connections and properties between electron density and electron localisation function data
    network.addConnection(MeshRenderer.getOutport('image'), Raycaster.getInport('bg'))
    network.addConnection(EntryExitPoints.getOutport('entry'), Raycaster.getInport('entry'))
    network.addConnection(EntryExitPoints.getOutport('exit'), Raycaster.getInport('exit'))
    network.addConnection(HDFsource.getOutport('outport'), HDFvolume.getInport('inport'))
    network.addConnection(HDFvolume.getOutport('outport'), BoundingBox.getInport('volume'))
    network.addConnection(HDFvolume.getOutport('outport'), CubeProxyGeometry.getInport('volume'))
    network.addConnection(HDFvolume.getOutport('outport'), Raycaster.getInport('volume'))
    network.addConnection(BoundingBox.getOutport('mesh'), MeshRenderer.getInport('geometry'))
    network.addConnection(CubeProxyGeometry.getOutport('proxyGeometry'), EntryExitPoints.getInport('geometry'))
    network.addConnection(Background.getOutport('outport'), Canvas.getInport('inport'))
    network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), EntryExitPoints.getPropertyByIdentifier('camera'))
    
    entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
    entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)
 
# Function for building a volume network for electron density data
def charge(h5file, iso=None, slice=False, xpos=0, ypos=0):
    """Creates an Inviwo network for electron charge density visualization
    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    iso : int
         (Default value = None)
        Iso-value for ISO Raycaster processor. None otherwise
    slice : bool
         (Default value = False)
        True if slice-function is enabled. False otherwise   
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor
    """
    
    volume='Charge raycaster'
    volume_network(h5file, volume, iso, slice, xpos, ypos)

# Function for building a volume network for electron localisation function data
# def elf(h5file, iso=None, slice=False, xpos=0, ypos=0):
    """
    Creates an Inviwo network for electron localization function data
    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    iso : int
         (Default value = None)
        Iso-value for ISO Raycaster processor. None otherwise
    slice : bool
         (Default value = False)
        True if slice-function is enabled. False otherwise   
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor
    """
    # volume='Elf raycaster'
    # volume_network(h5file, volume, iso, slice, xpos, ypos)

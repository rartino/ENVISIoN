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

import inviwo 
import inviwoqt
import numpy as np
import h5py
from .common import _add_h5source, _add_processor

# Function for buiding a volume network for both electron density and electron localisation function data
def volume_network(h5file, volume, iso, slice, xstart_pos, ystart_pos):
    # Shared processors, processor positions and base vectors between electron density and electron localisation function data
    HDFsource = _add_h5source(h5file, xstart_pos, ystart_pos)
    inviwo.setPropertyValue(HDFsource+'.filename', h5file)
    HDFvolume = _add_processor('org.inviwo.hdf5.ToVolume', 'HDF5 To Volume', xstart_pos, ystart_pos+75)  
    # Read base vectors
    with h5py.File(h5file,"r") as h5:
        basis_4x4=np.identity(4)
        basis_array=np.array(h5["/basis/"], dtype='d')
        basis_4x4[:3,:3]=basis_array           
    BoundingBox = _add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xstart_pos+200, ystart_pos+150)    
    MeshRenderer = _add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xstart_pos+200, ystart_pos+225)
    CubeProxyGeometry = _add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xstart_pos+30, ystart_pos+150)
    EntryExitPoints = _add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xstart_pos+30, ystart_pos+225)
    # Add processor for Volume or ISO Raycaster based on if "iso" is assigned a value or not and give it correct name based on the string "volume" assigned a value in function "charge" or "elf". 
    if iso==None:
        Raycaster = _add_processor('org.inviwo.VolumeRaycaster', volume, xstart_pos, ystart_pos+300) 
    else:
        Raycaster = _add_processor('org.inviwo.ISORaycaster', volume, xstart_pos, ystart_pos+300)
        inviwo.setPropertyValue(Raycaster+'.raycasting.isoValue', iso)
    # Add processors, connections and properties for slice function if slice=True and "iso" hasn't been assigned a value        
    if slice:
        if iso==None:
            VolumeSlice = _add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xstart_pos-170, ystart_pos+300)          
            ImageLayout = _add_processor('org.inviwo.ImageLayoutGL', 'Image Layout', xstart_pos, ystart_pos+375)     
            Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+450)
            Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+525)
            inviwo.addConnection(HDFvolume, 'outport', VolumeSlice, 'volume')
            inviwo.addConnection(VolumeSlice, 'outport', ImageLayout, 'multiinport')
            inviwo.addConnection(Raycaster, 'outport', ImageLayout, 'multiinport') 
            inviwo.addConnection(ImageLayout, 'outport', Background, 'inport')
            inviwo.setPropertyValue(ImageLayout+'.layout', 2)
            inviwo.addLink(VolumeSlice+'.planePosition', Raycaster+'.positionindicator.plane1.position')
            inviwo.addLink(VolumeSlice+'.planeNormal', Raycaster+'.positionindicator.plane1.normal')
            inviwo.setPropertyValue(Raycaster+'.positionindicator.enable', True)
            inviwo.setPropertyValue(Canvas+'.inputSize.dimensions', (700,300))
            inviwo.addPointToTransferFunction(VolumeSlice+'.tfGroup.transferFunction',(0.0,1.0),(0.0,0.0,1.0))
            inviwo.addPointToTransferFunction(VolumeSlice+'.tfGroup.transferFunction',(0.25,1.0),(0.0,1.0,1.0))
            inviwo.addPointToTransferFunction(VolumeSlice+'.tfGroup.transferFunction',(0.5,1.0),(0.0,1.0,0.0))
            inviwo.addPointToTransferFunction(VolumeSlice+'.tfGroup.transferFunction',(0.75,1.0),(1.0,1.0,0.0))
            inviwo.addPointToTransferFunction(VolumeSlice+'.tfGroup.transferFunction',(1.0,1.0),(1.0,0.0,0.0))
            inviwo.setPropertyValue(Raycaster+'.positionindicator.plane1.enable', True)
            inviwo.setPropertyValue(Raycaster+'.positionindicator.plane2.enable', False)
            inviwo.setPropertyValue(Raycaster+'.positionindicator.plane3.enable', False)
            inviwo.setPropertyValue(Raycaster+'.positionindicator.plane1.color', (1.0,1.0,1.0,0.5))
            inviwo.addPointToTransferFunction(Raycaster+'.transferFunction',(0.6,1.0),(0.0,1.0,1.0))
            inviwo.addPointToTransferFunction(Raycaster+'.transferFunction',(0.45,0.0),(0.0,0.0,1.0))
            inviwo.addPointToTransferFunction(Raycaster+'.transferFunction',(0.7,0.0),(0.0,0.0,0.0))
        else:
            print("Slice is not possible with ISO Raycasting, therefore no slice-function is showing.")
    # Add processors, connections and properties for no slice function if slice=False or "iso" has been assigned a value   
    if not slice or (slice and iso != None):
        Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+375)
        Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+450)
        inviwo.addConnection(Raycaster, 'outport', Background, 'inport') 
        inviwo.setPropertyValue(Canvas+'.inputSize.dimensions', (300,300))            
    # Shared connections and properties between electron density and electron localisation function data
    inviwo.addConnection(MeshRenderer, 'image', Raycaster, 'bg')
    inviwo.addConnection(EntryExitPoints, 'entry', Raycaster, 'entry')
    inviwo.addConnection(EntryExitPoints, 'exit', Raycaster, 'exit')   
    inviwo.addConnection(HDFsource, 'outport', HDFvolume, 'inport')
    inviwo.addConnection(HDFvolume, 'outport', BoundingBox, 'volume')
    inviwo.addConnection(HDFvolume, 'outport', CubeProxyGeometry, 'volume')
    inviwo.addConnection(HDFvolume, 'outport', Raycaster, 'volume')  
    inviwo.addConnection(BoundingBox, 'mesh', MeshRenderer, 'geometry')
    inviwo.addConnection(CubeProxyGeometry, 'proxyGeometry', EntryExitPoints, 'geometry')
    inviwo.addConnection(Background, 'outport', Canvas, 'inport')
    inviwo.setPropertyValue(HDFvolume+'.basisGroup.basis', tuple(map(tuple, basis_4x4)))
    inviwo.setPropertyValue(EntryExitPoints+'.camera.lookFrom', (0,0,8))
    # Set correct path to volume data
    if volume=='Charge raycaster':         
        inviwo.setPropertyValue(HDFvolume+'.volumeSelection', '/CHG/final')
    else:
        inviwo.setPropertyValue(HDFvolume+'.volumeSelection', '/ELF/final')
 
# Function for building a volume network for electron density data
def charge(h5file, iso, slice, xstart_pos, ystart_pos):
    volume='Charge raycaster'
    volume_network(h5file, volume, iso, slice, xstart_pos, ystart_pos)

# Function for building a volume network for electron localisation function data
def elf(h5file, iso, slice, xstart_pos, ystart_pos):
    volume='Elf raycaster'
    volume_network(h5file, volume, iso, slice, xstart_pos, ystart_pos)
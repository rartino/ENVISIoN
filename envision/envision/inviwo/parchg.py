#
#  ENVISIoN
#
#  Copyright (c) 2017-2018 David Hartman, Anders Rehult, Marian Brännvall, Andreas Kempe
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
#  Alterations to this file by Anders Rehult, Marian Brännvall
#  and Andreas Kempe
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import inviwopy
import numpy as np
import h5py
import math
from .common import _add_h5source, _add_processor

app = inviwopy.app
network = app.network

def merger_calc(l, previous_level):
    if previous_level != 1:
        level = math.ceil(previous_level/4)
        l.append(level)
        l = merger_calc(l,level)
    return l

# Function for buiding a volume network for both electron density and electron localisation function data (commented out)
def parchg(h5file, sli, parchg_list, xstart_pos=0, ystart_pos=0):
    """ Creates an Inviwo network for visualisation of volume data such as electron density or electron
            localisation function data.
    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    volume : str
        Specifies type of volume data to be visualised, electron density och ELF. 
    sli : bool
        True if slice-function is enabled. False otherwise   
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor
    """
    

    volume = 'Partial Charge Raycaster' 
    n = len(parchg_list)
    level_list = []
    level_list = merger_calc(level_list,n)

    HDFvolume_list = []
    merger_list = []
    
    # Shared processors, processor positions and base vectors between electron density and electron localisation function data
    HDFsource = _add_h5source(h5file, xstart_pos, ystart_pos)
    filenameProperty = HDFsource.getPropertyByIdentifier('filename')
    filenameProperty.value = h5file

    for i in range(0, n):
        HDFvolume_list.append(_add_processor('org.inviwo.hdf5.ToVolume', 'Band ' + str(parchg_list[i]), xstart_pos + 180*i, ystart_pos+75))
        scaling_factor = 1
        # Read base vectors
        with h5py.File(h5file,"r") as h5:
            basis_4x4=np.identity(4)
            basis_array=np.array(h5["/basis/"], dtype='d')
            basis_4x4[:3,:3]=basis_array
            scaling_factor = h5['/scaling_factor'].value

    for i in range(0, len(level_list)):
        submerger_list = []
        for j in range(0, level_list[i]):
            submerger_list.append(_add_processor('org.inviwo.VolumeMerger', 'Level ' + str(i+1) + '  unit ' + str(j+1), xstart_pos + 180*j, ystart_pos + 150 + 75*i))
        merger_list.append(submerger_list)
    
            
            
    
            
    BoundingBox = _add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xstart_pos+200, ystart_pos+150 + 75*len(level_list))    
    MeshRenderer = _add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xstart_pos+200, ystart_pos+225 + 75*len(level_list))
    CubeProxyGeometry = _add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xstart_pos+30, ystart_pos+150 + 75*len(level_list))
    EntryExitPoints = _add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xstart_pos+30, ystart_pos+225 + 75*len(level_list))
 

    Raycaster = _add_processor('org.inviwo.MultichannelRaycaster', volume, xstart_pos, ystart_pos+300 + 75*len(level_list))
    # Set colors and transparency
    
    raycaster_transferfunction_property = Raycaster.getPropertyByIdentifier('transfer-functions').getPropertyByIdentifier('transferFunction1')
    raycaster_transferfunction_property.clear()
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.0,0.01),inviwopy.glm.vec3(0.0,0.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.25,0.01),inviwopy.glm.vec3(0.0,1.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.5,0.01),inviwopy.glm.vec3(0.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.75,0.01),inviwopy.glm.vec3(1.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(1.0,0.01),inviwopy.glm.vec3(1.0,0.0,0.0))
    raycaster_transferfunction_property = Raycaster.getPropertyByIdentifier('transfer-functions').getPropertyByIdentifier('transferFunction2')
    raycaster_transferfunction_property.clear()
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.0,0.01),inviwopy.glm.vec3(0.0,0.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.25,0.01),inviwopy.glm.vec3(0.0,1.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.5,0.01),inviwopy.glm.vec3(0.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.75,0.01),inviwopy.glm.vec3(1.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(1.0,0.01),inviwopy.glm.vec3(1.0,0.0,0.0))
    raycaster_transferfunction_property = Raycaster.getPropertyByIdentifier('transfer-functions').getPropertyByIdentifier('transferFunction3')
    raycaster_transferfunction_property.clear()
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.0,0.01),inviwopy.glm.vec3(0.0,0.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.25,0.01),inviwopy.glm.vec3(0.0,1.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.5,0.01),inviwopy.glm.vec3(0.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.75,0.01),inviwopy.glm.vec3(1.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(1.0,0.01),inviwopy.glm.vec3(1.0,0.0,0.0))
    raycaster_transferfunction_property = Raycaster.getPropertyByIdentifier('transfer-functions').getPropertyByIdentifier('transferFunction4')
    raycaster_transferfunction_property.clear()
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.0,0.01),inviwopy.glm.vec3(0.0,0.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.25,0.01),inviwopy.glm.vec3(0.0,1.0,1.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.5,0.01),inviwopy.glm.vec3(0.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(0.75,0.01),inviwopy.glm.vec3(1.0,1.0,0.0))
    raycaster_transferfunction_property.addPoint(inviwopy.glm.vec2(1.0,0.01),inviwopy.glm.vec3(1.0,0.0,0.0))

    if sli:
 
        VolumeSlice = _add_processor('org.inviwo.VolumeSliceGL', 'Volume Slice', xstart_pos-170, ystart_pos+300)          
        ImageLayout = _add_processor('org.inviwo.ImageLayoutGL', 'Image Layout', xstart_pos, ystart_pos+375)     
        Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+450)
        Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+525)

        if merger_list:
            network.addConnection(merger_list[-1][0].getOutport('outputVolume'), VolumeSlice.getInport('volume'))
        else:
            network.addConnection(HDFvolume_list[0].getOutport('outport'), VolumeSlice.getInport('volume'))
        
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

    if not sli:

        Background = _add_processor('org.inviwo.Background', 'Background', xstart_pos, ystart_pos+375 + 75*len(level_list))
        Canvas = _add_processor('org.inviwo.CanvasGL', 'Canvas', xstart_pos, ystart_pos+450 + 75*len(level_list))
        network.addConnection(Raycaster.getOutport('outport'), Background.getInport('inport'))
        canvas_dimensions_property = Canvas.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimensions')
        canvas_dimensions_property.value = inviwopy.glm.ivec2(400,400)

    
    # Shared connections and properties between electron density and electron localisation function data
    network.addConnection(MeshRenderer.getOutport('image'), Raycaster.getInport('bg'))
    network.addConnection(EntryExitPoints.getOutport('entry'), Raycaster.getInport('entry'))
    network.addConnection(EntryExitPoints.getOutport('exit'), Raycaster.getInport('exit'))
    network.addConnection(BoundingBox.getOutport('mesh'), MeshRenderer.getInport('geometry'))
    network.addConnection(CubeProxyGeometry.getOutport('proxyGeometry'), EntryExitPoints.getInport('geometry'))
    network.addConnection(Background.getOutport('outport'), Canvas.getInport('inport'))
    network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), EntryExitPoints.getPropertyByIdentifier('camera'))


    #Connections from the source and the HDF52Volume blocks
    for i in range(0,n):
        network.addConnection(HDFsource.getOutport('outport'), HDFvolume_list[i].getInport('inport'))
        if merger_list:
            if ((i+1) % 4) == 1:
                network.addConnection(HDFvolume_list[i].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('inputVolume'))
            else:
                network.addConnection(HDFvolume_list[i].getOutport('outport'), merger_list[0][math.floor(i/4)].getInport('volume'+str((i%4)+1)))
    
    #Connections from the mergers
    if not merger_list:
         network.addConnection(HDFvolume_list[0].getOutport('outport'), BoundingBox.getInport('volume'))
         network.addConnection(HDFvolume_list[0].getOutport('outport'), CubeProxyGeometry.getInport('volume'))
         network.addConnection(HDFvolume_list[0].getOutport('outport'), Raycaster.getInport('volume'))
    else:
        for i in range(0, len(merger_list)):
            if (i + 1) != len(merger_list):
                for j in range(0, len(merger_list[i])):
                    if ((j+1) % 4) == 1:
                        network.addConnection(merger_list[i][j].getOutport('outputVolume'), merger_list[i+1][math.floor(j/4)].getInport('inputVolume'))
                    else:
                        network.addConnection(merger_list[i][j].getOutport('outputVolume'), merger_list[i+1][math.floor(j/4)].getInport('volume'+str((j%4)+1)))
        
        network.addConnection(merger_list[-1][0].getOutport('outputVolume'), BoundingBox.getInport('volume'))
        network.addConnection(merger_list[-1][0].getOutport('outputVolume'), CubeProxyGeometry.getInport('volume'))
        network.addConnection(merger_list[-1][0].getOutport('outputVolume'), Raycaster.getInport('volume'))
         
        
   
    
   
    # Set correct path to volume data
    

    for i in range(0, n):
        hdfvolume_volumeSelection_property = HDFvolume_list[i].getPropertyByIdentifier('volumeSelection')

        nonzeroes = math.ceil(math.log10(parchg_list[i])) 
        if nonzeroes == 1:
            hdfvolume_volumeSelection_property.value = '/PARCHG/Bands/000' + str(parchg_list[i])
        elif nonzeroes == 2:
            hdfvolume_volumeSelection_property.value = '/PARCHG/Bands/00' + str(parchg_list[i])
        elif nonzeroes == 3:
            hdfvolume_volumeSelection_property.value = '/PARCHG/Bands/0' + str(parchg_list[i])
        else:
            hdfvolume_volumeSelection_property.value = '/PARCHG/Bands/' + str(parchg_list[i])
        
        HDFvolume_basis_property = HDFvolume_list[i].getPropertyByIdentifier('basisGroup').getPropertyByIdentifier('basis')
        HDFvolume_basis_property.minValue = inviwopy.glm.mat4(-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000,
                                                              -1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000)
        HDFvolume_basis_property.maxValue = inviwopy.glm.mat4(1000,1000,1000,1000,1000,1000,1000,1000,
                                                              1000,1000,1000,1000,1000,1000,1000,1000)
        HDFvolume_basis_property.value = inviwopy.glm.mat4(scaling_factor * basis_4x4[0][0],scaling_factor * basis_4x4[0][1],scaling_factor * basis_4x4[0][2],
                                                           scaling_factor * basis_4x4[0][3],scaling_factor * basis_4x4[1][0],scaling_factor * basis_4x4[1][1],
                                                           scaling_factor * basis_4x4[1][2],scaling_factor * basis_4x4[1][3],scaling_factor * basis_4x4[2][0],
                                                           scaling_factor * basis_4x4[2][1],scaling_factor * basis_4x4[2][2],scaling_factor * basis_4x4[2][3],
                                                           scaling_factor * basis_4x4[3][0],scaling_factor * basis_4x4[3][1],scaling_factor * basis_4x4[3][2],
                                                           scaling_factor * basis_4x4[3][3])
        
    entryExitPoints_lookFrom_property = EntryExitPoints.getPropertyByIdentifier('camera').getPropertyByIdentifier('lookFrom')
    entryExitPoints_lookFrom_property.value = inviwopy.glm.vec3(0,0,8)

    # Connect unit cell and volume visualisation.
    UnitCellRenderer = network.getProcessorByIdentifier('Unit Cell Renderer')
    if UnitCellRenderer:
        network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
        network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
        network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))


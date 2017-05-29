#
#  ENVISIoN
#
#  Copyright (c) 2017 Josef Adamsson
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
from .common import _add_processor, _add_h5source
from .data import atomic_radii, ionic_radii, element_names, element_colors

  
def _cellnetwork(h5file, md=False, xpos=0, ypos=0):
    HDFsource = _add_h5source(h5file, xpos, ypos)
    
    meshRend = _add_processor('org.inviwo.SphereRenderer', 'Unit Cell Renderer', xpos, ypos+300)
            
    canvas = _add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', xpos, ypos+400)
    inviwo.addConnection(meshRend, 'image', canvas, 'inport')
    strucMesh = _add_processor('envision.StructureMesh', 'Unit Cell Mesh', xpos, ypos+200)
    inviwo.setPropertyValue(strucMesh+'.fullMesh', False)
    inviwo.addConnection(strucMesh, 'mesh', meshRend, 'geometry')
    
    with h5py.File(h5file,"r") as h5:
        basis_matrix = np.array(h5["/basis"], dtype='d')
        inviwo.setPropertyValue(strucMesh+'.basis', tuple(map(tuple, basis_matrix)))        
        inviwo.setPropertyValue(strucMesh+'.timestep',0)
        inviwo.setPropertyMinValue(strucMesh+'.timestep',0)
        timesteps=0
        base_group = "/UnitCell"
        if md:
            base_group = "/MD"
            animator = _add_processor('org.inviwo.OrdinalPropertyAnimator','MD animation', xpos+200, ypos+200)
            timesteps = h5[base_group].attrs['steps']
            inviwo.setPropertyValue(strucMesh+'.animation', True)
            inviwo.setPropertyValue(animator+'.property',8) # IntProperty
            inviwo.setPropertyValue(animator+'.OrgInviwoIntProperty',0)
            inviwo.setPropertyMinValue(animator+'.OrgInviwoIntProperty',0)
            inviwo.setPropertyMaxValue(animator+'.OrgInviwoIntProperty',timesteps)
            inviwo.setPropertyMaxValue(animator+'.delay',10)
            inviwo.addLink(animator+'.OrgInviwoIntProperty',strucMesh+'.timestep')
            inviwo.setPropertyValue(animator+'.OrgInviwoIntProperty-Delta',1)            
        inviwo.setPropertyMaxValue(strucMesh+'.timestep',timesteps)

        species = len(h5[base_group + "/Atoms"].keys()) - 1
        for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
            element = h5[base_group + "/Atoms/"+key].attrs['element']            
            name = element_names.get(element, 'Unknown')
            color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
            radius = atomic_radii.get(element, 0.5)/100
            coordReader = _add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos+int((i-species/2)*200), ypos+100)
            inviwo.addConnection(HDFsource, 'outport', coordReader, 'inport')           
            inviwo.addConnection(coordReader, 'outport', strucMesh, 'coordinates')
            inviwo.setPropertyValue(coordReader+'.path', base_group + '/Atoms/'+key)
            inviwo.setPropertyValue(strucMesh+'.radius{0}'.format(i), radius)
            inviwo.setPropertyValue(strucMesh+'.color{0}'.format(i), color)
            if md:
                atoms = int(h5["/MD/Atoms/"+key].attrs['atoms'])
            else:
                atoms = 0
            inviwo.setPropertyValue(strucMesh+'.atoms{0}'.format(i), atoms)
            inviwo.setPropertyMinValue(strucMesh+'.atoms{0}'.format(i), atoms)
            inviwo.setPropertyMaxValue(strucMesh+'.atoms{0}'.format(i), atoms)
  
def md(h5file, xpos=0, ypos=0):
    """Creates an Inviwo network for MD visualization

    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor

    """
    _cellnetwork(h5file, True, xpos, ypos)
    
def unitcell(h5file, xpos=0, ypos=0):
    """Creates an Inviwo network for unit cell visualization

    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor

    """
    _cellnetwork(h5file, False, xpos, ypos)

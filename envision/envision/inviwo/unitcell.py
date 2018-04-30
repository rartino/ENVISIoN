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
import inviwopy
import numpy as np
import h5py
from .common import _add_processor, _add_h5source, _add_property
from .data import atomic_radii, element_names, element_colors

app = inviwopy.app
network = app.network

def _cellnetwork(h5file, md=False, xpos=0, ypos=0):
    HDFsource = _add_h5source(h5file, xpos, ypos)

    meshRend = _add_processor('org.inviwo.SphereRenderer', 'Unit Cell Renderer', xpos, ypos+300)

    canvas = _add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', xpos, ypos+400)
    imageOutport = meshRend.getPort('image')
    imageInport = canvas.getInport('inport')
    network.addConnection(imageOutport, imageInport)

    strucMesh = _add_processor('envision.StructureMesh', 'Unit Cell Mesh', xpos, ypos+200)
    fullMesh = strucMesh.getPropertyByIdentifier('fullMesh')
    fullMesh.value = False
    meshPort = strucMesh.getOutport('mesh')
    geometryPort = meshRend.getInport('geometry')
    network.addConnection(meshPort, geometryPort)

    with h5py.File(h5file,"r") as h5:
        basis_matrix = np.array(h5["/basis"], dtype='d')
        strucMesh_basis_property = strucMesh.getPropertyByIdentifier('basis')
        strucMesh_basis_property.minValue = inviwopy.glm.mat3(-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000)
        strucMesh_basis_property.maxValue = inviwopy.glm.mat3(1000,1000,1000,1000,1000,1000,1000,1000,1000)
        strucMesh_basis_property.value = inviwopy.glm.mat3(basis_matrix[0,0],basis_matrix[0,1],basis_matrix[0,2],basis_matrix[1,0],basis_matrix[1,1],basis_matrix[1,2],basis_matrix[2,0],basis_matrix[2,1],basis_matrix[2,2])
        strucMesh_scaling_factor_property = strucMesh.getPropertyByIdentifier('scalingFactor')
        strucMesh_scaling_factor_property.maxValue = h5['/scaling_factor'].value
        strucMesh_scaling_factor_property.value = h5['/scaling_factor'].value
        strucMesh_timestep_property = strucMesh.getPropertyByIdentifier('timestep')
        strucMesh_timestep_property.value = 0
        strucMesh_timestep_property.minValue = 0
        timesteps=0
        base_group = "/UnitCell"
        if md:
            base_group = "/MD"
            animator = _add_processor('org.inviwo.OrdinalPropertyAnimator','MD animation', xpos+200, ypos+200)
            timesteps = h5[base_group].attrs['steps']
            strucMesh_animation_property = strucMesh.getPropertyByIdentifier('animation')
            strucMesh_animation_property.value = True
            int_property = _add_property('org.inviwo.OrdinalAnimationProperty.Int', 'intProperty', animator)
            int_property_value = int_property.getPropertyByIdentifier('value')
            int_property_value.value = 0
            int_property_value.minValue = 0
            int_property_value.maxValue = timesteps
            animator_delay_property.maxValue = 10
            network.addLink(animator.getPropertyByIdentifier(''), strucMesh.getPropertyByIdentifier('timestep'))
            int_property_delta = int_property.getPropertyByIdentifier('delta')
            int_property_delta.value = 1
        strucMesh_timestep_property.maxValue = timesteps
        species = len(h5[base_group + "/Atoms"].keys()) - 1
        for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
            element = h5[base_group + "/Atoms/"+key].attrs['element']
            name = element_names.get(element, 'Unknown')
            color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
            radius = atomic_radii.get(element, 0.5)
            coordReader = _add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos+int((i-species/2)*200), ypos+100)
            network.addConnection(HDFsource.getOutport('outport'), coordReader.getInport('inport'))
            network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
            coordReader_path_property = coordReader.getPropertyByIdentifier('path')
            coordReader_path_property.value = base_group + '/Atoms/' + key
            strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))

            #strucMesh_radius_property.maxValue = 3
            strucMesh_radius_property.value = radius
            strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
            strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])
            if md:
                atoms = int(h5["/MD/Atoms/"+key].attrs['atoms'])
            else:
                atoms = 0
            strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
            strucMesh_atom_property.value = atoms
            strucMesh_atom_property.minValue = atoms
            strucMesh_atom_property.maxValue = atoms

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

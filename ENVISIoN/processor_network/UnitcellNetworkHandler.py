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
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
from matplotlib import pyplot as plt 
import h5py
from .data import atomic_radii, element_names, element_colors

from .NetworkHandler import NetworkHandler

class UnitcellNetworkHandler(NetworkHandler):
    """ Base class for setting up and handling a self.network for generic unitcell rendering for ENVISIoN.
    Does not build a complete self.network by itself. Need to be supplied with hdf5 data from somewhere.
    Do not use directly, inherited in other classes for handling specific visualizations.
    """
    def __init__(self, hdf5_path, inviwoApp):
        NetworkHandler.__init__(self, inviwoApp)
        self.nAtomTypes = 0
        self.atomNames = []
        # Make sure the hdf5 file is valid
        with h5py.File(hdf5_path, 'r') as file:
            if file.get("UnitCell") == None:
                raise AssertionError("No unitcell data in that file")

        
        self.setup_unitcell_network(hdf5_path)


# ------------------------------------------
# ------- Property control functions -------

    def set_atom_radius(self, radius, index=None):
        structureMesh = self.get_processor('Unit Cell Mesh')
        if structureMesh.fullMesh.value:
            if index != None:
                structureMesh.getPropertyByIdentifier("radius" + str(index)).value = radius
            else:
                for i in range(self.nAtomTypes):
                    self.set_atom_radius(radius, i)
        else:
            sphereRenderer = self.get_processor('Unit Cell Renderer')
            sphereRenderer.sphereProperties.defaultRadius.value = radius
        return [True, None]


    def hide_atoms(self, hide):
        if hide:
            return self.set_atom_radius(0)
        else:
            return self.set_atom_radius(0.5)
    
    def get_atom_names(self):
        return [True, self.atomNames]
    
    def get_atom_name(self, index):
        return [True, self.atomNames[index]]


    def toggle_unitcell_canvas(self, enable_unitcell):
    # Add or remove the unitcell canvas
        
        unitcellCanvas = self.get_processor('Unit Cell Canvas')
        unitcellRenderer = self.get_processor('Unit Cell Renderer')
        # If already in correct mode dont do anything
        if (unitcellCanvas and enable_unitcell) or (not unitcellCanvas and not enable_unitcell):
            return

        if enable_unitcell:
            unitcellCanvas = self.add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', -600, 400)
            unitcellCanvas.inputSize.dimensions.value = inviwopy.glm.ivec2(500, 500)
            self.network.addConnection(unitcellRenderer.getOutport('image'), unitcellCanvas.getInport('inport'))
        else:
            self.remove_processor('Unit Cell Canvas')
        return [True, None]

    def toggle_full_mesh(self, enable):
        
        structMesh = self.get_processor('Unit Cell Mesh')
        structMesh.fullMesh.value = enable
        return [True, None]

    def set_canvas_position(self, x, y):
    # Updates the position of the canvas
    # Upper left corner will be at coordinate (x, y)
        
        unitcellCanvas = self.get_processor('Unit Cell Canvas')
        if not unitcellCanvas:
            return
        unitcellCanvas.position.value = inviwopy.glm.ivec2(x, y)
        return [True, None]
# ------------------------------------------
# ------- Network building functions -------

    def setup_unitcell_network(self, h5file):
        
        xpos = -600
        ypos = 0

        HDFsource = self.add_h5source(h5file, xpos, ypos)

        meshRenderer = self.add_processor('org.inviwo.SphereRenderer', 'Unit Cell Renderer', xpos, ypos+300)
        canvas = self.add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', xpos, ypos+400)
        self.network.addConnection(meshRenderer.getPort('image'), canvas.getInport('inport'))

        strucMesh = self.add_processor('envision.StructureMesh', 'Unit Cell Mesh', xpos, ypos+200)
        # Activate fullMesh, this allows individual resizing of atoms and centers the unitcell around same origin as volume
        strucMesh.fullMesh.value = False

        self.network.addConnection(strucMesh.getOutport('mesh'), meshRenderer.getInport('geometry'))

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

            strucMesh_timestep_property.maxValue = timesteps
            species = len(h5[base_group + "/Atoms"].keys()) - 1
            for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
                element = h5[base_group + "/Atoms/"+key].attrs['element']
                name = element_names.get(element, 'Unknown')
                self.atomNames.append(name)
                color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
                radius = atomic_radii.get(element, 0.5)
                coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos+int((i-species/2)*200), ypos+100)
                self.network.addConnection(HDFsource.getOutport('outport'), coordReader.getInport('inport'))
                self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                coordReader_path_property = coordReader.getPropertyByIdentifier('path')
                coordReader_path_property.value = base_group + '/Atoms/' + key
                strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                # The atoms in a crystal don't actually look like spheres, as the valence electrons are shared across the crystal.
                # The different radii of the elements in data.py are just to differentiate between different elements.
                strucMesh_radius_property.maxValue = 10
                strucMesh_radius_property.value = radius
                strucMesh_radius_property.value = 0.3
                strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])

                atoms = 0
                strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                strucMesh_atom_property.value = atoms
                strucMesh_atom_property.minValue = atoms
                strucMesh_atom_property.maxValue = atoms

                self.nAtomTypes += 1
       
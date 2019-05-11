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
from data import atomic_radii, element_names, element_colors

class UnitcellNetworkHandler():
    """ Base class for setting up and handling a network for generic unitcell rendering for ENVISIoN.
    Does not build a complete network by itself. Need to be supplied with hdf5 data from somewhere.
    Do not use directly, inherited in other classes for handling specific visualizations.
    """
    def __init__(self, hdf5_path):
        # Make sure the hdf5 file is valid
        with h5py.File(hdf5_path, 'r') as file:
            if file.get("UnitCell") == None:
                raise AssertionError("No unitcell data in that file")

        self.nAtomTypes = 0
        self.atomNames = []
        self.setup_unitcell_network(hdf5_path)
        self.toggle_unitcell_canvas(False)


# ------------------------------------------
# ------- Property control functions -------

    def set_atom_radius(self, radius, index=None):
        network = inviwopy.app.network
        structureMesh = network.getProcessorByIdentifier('Unit Cell Mesh')
        if index != None:
            structureMesh.getPropertyByIdentifier("radius" + str(index)).value = radius
        else:
            for i in range(self.nAtomTypes):
                self.set_atom_radius(radius, i)

    def hide_atoms(self, hide):
        if hide:
            self.set_atom_radius(0)
        else:
            self.set_atom_radius(0.1)
    
    def get_atom_name(self, index):
        return self.atomNames[index]


    def toggle_unitcell_canvas(self, enable_unitcell):
    # Add or remove the unitcell canvas
        network = inviwopy.app.network

        unitcellCanvas = network.getProcessorByIdentifier('Unit Cell Canvas')

        # If already in correct mode dont do anything
        if (unitcellCanvas and enable_unitcell) or (not unitcellCanvas and not enable_unitcell):
            return

        if enable_unitcell:
            SliceCanvas = _add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', -600, 400)
            SliceCanvas.inputSize.dimensions.value = inviwopy.glm.ivec2(200, 200)       
            network.addConnection(network.getProcessorByIdentifier('SliceBackground').getOutport('outport'), SliceCanvas.getInport('inport'))
        else:
            network.removeProcessor(unitcellCanvas)

# ------------------------------------------
# ------- Network building functions -------

    def clear_processor_network(self):
        network = inviwopy.app.network
        network.clear()

    def setup_unitcell_network(self, h5file):
        print("Building unitcell network")
        network = inviwopy.app.network
        xpos = -600
        ypos = 0

        HDFsource = _add_h5source(h5file, xpos, ypos)

        meshRenderer = _add_processor('org.inviwo.SphereRenderer', 'Unit Cell Renderer', xpos, ypos+300)
        canvas = _add_processor('org.inviwo.CanvasGL', 'Unit Cell Canvas', xpos, ypos+400)
        network.addConnection(meshRenderer.getPort('image'), canvas.getInport('inport'))

        strucMesh = _add_processor('envision.StructureMesh', 'Unit Cell Mesh', xpos, ypos+200)
        # Activate fullMesh, this allows individual resizing of atoms and centers the unitcell around same origin as volume
        strucMesh.fullMesh.value = True

        network.addConnection(strucMesh.getOutport('mesh'), meshRenderer.getInport('geometry'))

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
                coordReader = _add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos+int((i-species/2)*200), ypos+100)
                network.addConnection(HDFsource.getOutport('outport'), coordReader.getInport('inport'))
                network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
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
        
        # Connect unit cell and volume visualisation.
        volumeRend = network.getProcessorByIdentifier('Mesh Renderer')
        if volumeRend:
            network.addConnection(meshRenderer.getOutport('image'), volumeRend.getInport('imageInport'))
            network.addLink(meshRenderer.getPropertyByIdentifier('camera'), volumeRend.getPropertyByIdentifier('camera'))
            network.addLink(volumeRend.getPropertyByIdentifier('camera'), meshRenderer.getPropertyByIdentifier('camera'))
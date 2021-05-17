##  ENVISIoN
##
##  Copyright (c) 2021 Gabriel Anderberg, Didrik Axén,  Adam Engman,
##  Kristoffer Gubberud Maras, Joakim Stenborg
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice, this
##  list of conditions and the following disclaimer.
##  2. Redistributions in binary form must reproduce the above copyright notice,
##  this list of conditions and the following disclaimer in the documentation
##  and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
##  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## ##############################################################################################

import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from envisionpy.utils.atomData import atomic_radii, element_names, element_colors
from .baseNetworks.Decoration import Decoration

class Test(Decoration):
    '''
    Manages a subnetwork for atom position rendering.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0):
        Decoration.__init__(self, inviwoApp)
        self.atom_radii = []
        self.atom_names = []
        self.nAtomTypes = 0
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos)


        self.hide()

    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("UnitCell") != None

    def valid_visualisations(self):
        return ['charge', 'elf', 'parchg']

    def connect_decoration(self, other, vis_type):
        # Add a decoration by connecting data ports and linking properties.
        if vis_type not in self.valid_visualisations():
            raise EnvisionError('Invalid visualisation type ['+vis_type+'].')

        self.other_subnetworks[vis_type] = other

        # Link needed properties between networks.
        if vis_type == "force":
            self.network.addLink(other.camera_prop, self.camera_prop)
            self.network.addLink(self.camera_prop, other.camera_prop)
            other.camera_prop.invalidate()
            print(dir(self.camera_prop))

        other.connect_decoration_ports(self.decoration_outport)

    def disconnect_decoration(self, other, vis_type):
        if vis_type == 'charge' or vis_type == 'elf' or vis_type == 'parchg':
            self.network.removeLink(self.camera_prop, other.camera_prop)
        other.disconnect_decorations_port(self.decoration_outport)



    def get_ui_data(self):
        return [
            self.atom_names,
            self.atom_radii
        ]
# ------------------------------------------
# ------- Property control functions -------



    def hide_atoms(self):
        return self.set_atom_radius(0)

    def hide(self):
        return 0

# ------------------------------------------
# ------- Network building functions -------

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        strucMesh = self.add_processor('envision.StructureMesh', 'UnitcellMesh', xpos, ypos+3)




        with h5py.File(hdf5_path, "r") as h5:
            # Set basis matrix and scaling
            basis_matrix = np.array(h5["/basis"], dtype='d')
            strucMesh.basis.minValue = inviwopy.glm.mat3(
                -1000, -1000, -1000,
                -1000, -1000, -1000,
                -1000, -1000, -1000)
            strucMesh.basis.maxValue = inviwopy.glm.mat3(
                1000,1000,1000,
                1000,1000,1000,
                1000,1000,1000)
            strucMesh.basis.value = inviwopy.glm.mat3(
                basis_matrix[0,0], basis_matrix[0,1], basis_matrix[0,2],
                basis_matrix[1,0], basis_matrix[1,1], basis_matrix[1,2],
                basis_matrix[2,0], basis_matrix[2,1], basis_matrix[2,2])
            strucMesh.scalingFactor.maxValue = h5['/scaling_factor'][()]
            strucMesh.scalingFactor.value = h5['/scaling_factor'][()]


            base_group = "/UnitCell"

            for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
                element = h5[base_group + "/Atoms/"+key].attrs['element']
                print(element)
                name = element_names.get(element, 'Unknown')
                print(name)
                color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))


                radius = atomic_radii.get(element, 0.5)
                print(radius)
                self.atom_names.append(name)
                self.atom_radii.append(radius)

                coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos-i*7, ypos)
                self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
                self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                coordReader.path.value = base_group + '/Atoms/' + key

                if strucMesh.getPropertyByIdentifier('radius{0}'.format(i)) == None:
                        continue
                strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                strucMesh_radius_property.maxValue = 10
                strucMesh_radius_property.minValue = 0.001
                strucMesh_radius_property.value = radius

                strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])

                strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                print('atoms{0}'.format(i))
                strucMesh_atom_property.value = 0
                strucMesh_atom_property.minValue = 0
                strucMesh_atom_property.maxValue = 0

                self.nAtomTypes += 1

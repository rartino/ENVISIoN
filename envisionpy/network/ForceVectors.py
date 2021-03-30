import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from envisionpy.utils.atomData import atomic_radii, element_names, element_colors
from .baseNetworks.Decoration import Decoration

class ForceVectors(Decoration):
    '''
    Manages a subnetwork for atom position rendering.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0):
        Decoration.__init__(self, inviwoApp)
        self.atom_radii = []
        self.atom_names = []
        self.nAtomTypes = 0
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos)

        self.set_atom_radius(0.5)
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
        if vis_type == "force":
            self.network.removeLink(self.camera_prop, other.camera_prop)
        other.disconnect_decorations_port(self.decoration_outport)

    def show(self):
        self.get_processor('UnitcellCanvas').widget.show()

    def hide(self):
        self.get_processor('UnitcellCanvas').widget.hide()

    def get_ui_data(self):
        return [
            self.atom_names,
            self.atom_radii
        ]
# ------------------------------------------
# ------- Property control functions -------

    def set_atom_radius(self, radius, index=None):
        structureMesh = self.get_processor('UnitcellMesh')
        if structureMesh.fullMesh.value:
            if index != None:
                self.atom_radii[index] = radius
                structureMesh.getPropertyByIdentifier("radius" + str(index)).value = radius
            else:
                for i in range(self.nAtomTypes):
                    self.atom_radii[i] = radius
                    self.set_atom_radius(radius, i)
        else:
            sphereRenderer = self.get_processor('UnitcellRenderer')
            sphereRenderer.sphereProperties.defaultRadius.value = radius
            for i in range(self.nAtomTypes):
                self.atom_radii[i] = radius

    def hide_atoms(self):
        return self.set_atom_radius(0)

    def toggle_full_mesh(self, enable):
        structMesh = self.get_processor('UnitcellMesh')
        structMesh.fullMesh.value = enable

    def set_canvas_position(self, x, y):
    # Updates the position of the canvas
    # Upper left corner will be at coordinate (x, y)
        unitcellCanvas = self.get_processor('UnitcellCanvas')
        unitcellCanvas.position.value = inviwopy.glm.ivec2(x, y)

# ------------------------------------------
# ------- Network building functions -------

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        strucMesh = self.add_processor('envision.StructureMesh', 'UnitcellMesh', xpos, ypos+3)
        meshRenderer = self.add_processor('org.inviwo.SphereRenderer', 'UnitcellRenderer', xpos, ypos+6)
        background = self.add_processor('org.inviwo.Background', 'AtomBackground', xpos, ypos+9)
        canvas = self.add_processor('org.inviwo.CanvasGL', 'UnitcellCanvas', xpos, ypos+12)

        canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)

        self.network.addConnection(strucMesh.getOutport('mesh'), meshRenderer.getInport('geometry'))
        self.network.addConnection(meshRenderer.getOutport('image'), background.getInport('inport'))
        self.network.addConnection(background.getOutport('outport'), canvas.getInport('inport'))

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

            # Setup animation?
            strucMesh.timestep.value = 0
            strucMesh.timestep.minValue = 0
            base_group = "/UnitCell"

            strucMesh.timestep.maxValue = 0
            for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
                element = h5[base_group + "/Atoms/"+key].attrs['element']

                name = element_names.get(element, 'Unknown')
                color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
                radius = atomic_radii.get(element, 0.5)
                self.atom_names.append(name)
                self.atom_radii.append(radius)

                coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos-i*7, ypos)
                self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
                self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                coordReader.path.value = base_group + '/Atoms/' + key

                if strucMesh.getPropertyByIdentifier('radius{0}'.format(i)) == None:
                        continue
                strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                # The atoms in a crystal don't actually look like spheres, as the valence electrons are shared across the crystal.
                # The different radii of the elements in data.py are just to differentiate between different elements.
                strucMesh_radius_property.maxValue = 10
                strucMesh_radius_property.value = radius
                strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])

                strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                strucMesh_atom_property.value = 0
                strucMesh_atom_property.minValue = 0
                strucMesh_atom_property.maxValue = 0

                self.nAtomTypes += 1

        self.decoration_outport = meshRenderer.getOutport('image')
        # self.decoration_inport =
        self.decoration_inport = meshRenderer.getInport('imageInport')
        self.camera_prop = meshRenderer.camera

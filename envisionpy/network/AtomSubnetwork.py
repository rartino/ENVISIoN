import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from envisionpy.utils.atomData import atomic_radii, element_names, element_colors
from .Subnetwork import Subnetwork
# TODO add volume merger and multi-raycaster

class AtomSubnetwork(Subnetwork):
    '''
    Manages a subnetwork for atom position rendering.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0):
        Subnetwork.__init__(self, inviwoApp)


        self.atom_radii = []
        self.atom_names = []
        self.nAtomTypes = 0
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos)

    
    @staticmethod
    def check_hdf5(hdf5_path):
        with h5py.File(hdf5_path, 'r') as file: 
            if file.get("UnitCell") == None:
               return False 
        return True
# ------------------------------------------
# ------- Network building functions -------

    def link_camera(self, camera_prop):
        pass

    def connect_decoration(self, image_outport):
        pass

    def connect_hdf5(self, handle_outport):
        pass



    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        strucMesh = self.add_processor('envision.StructureMesh', 'UnitcellMesh', xpos, ypos+3)
        meshRenderer = self.add_processor('org.inviwo.SphereRenderer', 'Unit Cell Renderer', xpos, ypos+6)

        canvas = self.add_processor('org.inviwo.CanvasGL', 'UnitcellCanvas', xpos, ypos+9)
        
        canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)

        self.network.addConnection(strucMesh.getOutport('mesh'), meshRenderer.getInport('geometry'))
        self.network.addConnection(meshRenderer.getPort('image'), canvas.getInport('inport'))

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
                self.atom_names.append(name)
                color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
                radius = atomic_radii.get(element, 0.5)
                self.atom_radii.append(radius)
                
                coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos-i*7, ypos)
                self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
                self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                coordReader.path.value = base_group + '/Atoms/' + key
                strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                # The atoms in a crystal don't actually look like spheres, as the valence electrons are shared across the crystal.
                # The different radii of the elements in data.py are just to differentiate between different elements.
                print("A: ", 'radius{0}'.format(i))
                print(strucMesh_radius_property)
                print(strucMesh.radius0)
                strucMesh_radius_property.maxValue = 10
                print("B")
                strucMesh_radius_property.value = radius
                strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])

                strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                strucMesh_atom_property.value = 0
                strucMesh_atom_property.minValue = 0
                strucMesh_atom_property.maxValue = 0

                self.nAtomTypes += 1


        
        self.camera_prop = meshRenderer.camera
        # # Connect unitcell and volume visualisation.
        # try:
        #     UnitCellRenderer = self.get_processor('Unit Cell Renderer')
        # except ProcessorNotFoundError:
        #     print("No unitcell processor active")
        # else:
        #     self.network.addConnection(UnitCellRenderer.getOutport('image'), MeshRenderer.getInport('imageInport'))
        #     self.network.addLink(UnitCellRenderer.getPropertyByIdentifier('camera'), MeshRenderer.getPropertyByIdentifier('camera'))
        #     self.network.addLink(MeshRenderer.getPropertyByIdentifier('camera'), UnitCellRenderer.getPropertyByIdentifier('camera'))

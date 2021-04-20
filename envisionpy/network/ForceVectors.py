import inviwopy
import numpy as np
import h5py
import time
from envisionpy.utils.exceptions import *
from envisionpy.utils.atomData import atomic_radii, element_names, element_colors
from .baseNetworks.Decoration import Decoration
import time

class ForceVectors(Decoration):
    '''
    Manages a subnetwork for atom force rendering.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0, inviwo=False):
        Decoration.__init__(self, inviwoApp)
        self.atom_radii = []
        self.atom_names = []
        self.nAtomTypes = 0
        self.inviwo = inviwo
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos, bool)
        self.toggle_full_mesh(True)


    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("UnitCell") != None

    def valid_visualisations(self):
        return ['charge', 'elf', 'parchg', 'force']

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

    def show_vectors(self):
        meshRenderer = self.get_processor('UnitcellRenderer')
        vectorRenderer = self.get_processor('VectorRenderer')
        atomRenderer = self.get_processor('AtomRenderer')
        if self.inviwo:
            self.network.addConnection(vectorRenderer.getOutport('image'),meshRenderer.getInport('imageInport'))
        else:
            self.network.addConnection(vectorRenderer.getOutport('image'),atomRenderer.getInport('imageInport'))

    def hide_vectors(self):
        meshRenderer = self.get_processor('UnitcellRenderer')
        vectorRenderer = self.get_processor('VectorRenderer')
        atomRenderer = self.get_processor('AtomRenderer')
        if self.inviwo:
            self.network.removeConnection(vectorRenderer.getOutport('image'),meshRenderer.getInport('imageInport'))
        else:
            self.network.removeConnection(vectorRenderer.getOutport('image'),atomRenderer.getInport('imageInport'))

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

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos, bool):
        strucMesh = self.add_processor('envision.StructureMesh', 'UnitcellMesh', xpos, ypos+3)
        meshRenderer = self.add_processor('org.inviwo.SphereRenderer', 'UnitcellRenderer', xpos, ypos+6)
        background = self.add_processor('org.inviwo.Background', 'AtomBackground', xpos, ypos+9)
        vectorRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'VectorRenderer', xpos+7, ypos+6)
        canvas = self.add_processor('org.inviwo.CanvasGL', 'UnitcellCanvas', xpos, ypos+12)
        canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(1000,1000)
        self.network.addConnection(strucMesh.getOutport('mesh'), meshRenderer.getInport('geometry'))
        self.network.addConnection(meshRenderer.getOutport('image'), background.getInport('inport'))
        self.network.addConnection(background.getOutport('outport'), canvas.getInport('inport'))
        self.network.addConnection(vectorRenderer.getOutport('image'),meshRenderer.getInport('imageInport'))
        self.network.addLink(vectorRenderer.camera, meshRenderer.camera)
        self.network.addLink(meshRenderer.camera, vectorRenderer.camera)
        print(bool)
        with h5py.File(hdf5_path, "r") as h5:
            strucMesh.basis.value = inviwopy.glm.mat3(
                1, 0, 0,
                0, 1, 0,
                0, 0, 1)
            base_group = "/UnitCell"
            force_group = "/Forces"
            '''
            Utkommenterat är för framtida composite implementering
            '''
            for i,key in enumerate(list(h5[force_group + "/Atoms"].keys())):
                for p,n in enumerate(h5[force_group + "/Atoms/"+key]):
                    meshCreate = self.add_processor('org.inviwo.MeshCreator', '{0} {1}'.format(i, p), xpos+7, ypos)
                    self.network.addConnection(meshCreate.getOutport('outport'), vectorRenderer.getInport('geometry'))
                    self.network.addLink(meshCreate.camera, meshRenderer.camera)
                    self.network.addLink(meshRenderer.camera, meshCreate.camera)
                    meshCreate.meshType.selectedIndex = 10
                    meshCreate.scale.value = 0.01
                    meshCreate.color.value = inviwopy.glm.vec4(0.643, 0, 0, 1)
                    meshCreate.position1.value = inviwopy.glm.vec3(n[3]-0.5, n[4]-0.5, n[5]-0.5)
                    meshCreate.position2.value = inviwopy.glm.vec3(n[0]-0.5, n[1]-0.5, n[2]-0.5)
                    meshCreate.meta.selected = True
            self.network.replaceSelectionWithCompositeProcessor()
            if self.inviwo:
                for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
                    element = h5[base_group + "/Atoms/"+key].attrs['element']
                    name = element_names.get(element, 'Unknown')
                    color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
                    radius = atomic_radii.get(element, 0.5)
                    self.atom_names.append(name)
                    self.atom_radii.append(radius)
                    y = list(color)
                    y[3] = 0.7
                    color = tuple(y)
                    coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,name), xpos-i*7, ypos)
                    self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
                    self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                    coordReader.path.value = base_group + '/Atoms/' + key
                    if strucMesh.getPropertyByIdentifier('radius{0}'.format(i)) == None:
                            continue
                    strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                    strucMesh_radius_property.maxValue = 10
                    print(radius)
                    strucMesh_radius_property.value = radius/30
                    strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                    strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])
                    strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                    strucMesh_atom_property.value = 0
                    strucMesh_atom_property.minValue = 0
                    strucMesh_atom_property.maxValue = 0
                    self.nAtomTypes += 1
            else:
                atomRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'AtomRenderer', xpos+7, ypos+9)
                self.network.removeConnection(meshRenderer.getOutport('image'), background.getInport('inport'))
                self.network.addConnection(vectorRenderer.getOutport('image'),atomRenderer.getInport('imageInport'))

                self.network.addConnection(atomRenderer.getOutport('image'),background.getInport('inport'))
                self.network.addLink(atomRenderer.camera, meshRenderer.camera)
                self.network.addLink(meshRenderer.camera, atomRenderer.camera)
                for i,key in enumerate(list(h5[base_group + "/Atoms"].keys())):
                    element = h5[base_group + "/Atoms/"+key].attrs['element']
                    color = element_colors.get(element, (0.5, 0.5, 0.5, 1.0))
                    radius = atomic_radii.get(element, 0.5)
                    for p,n in enumerate(h5[base_group + "/Atoms/"+key]):
                        meshCreate = self.add_processor('org.inviwo.MeshCreator', '{0} {1} {2}'.format(p, i, "boll"), xpos, ypos)
                        self.network.addConnection(meshCreate.getOutport('outport'), atomRenderer.getInport('geometry'))
                        self.network.addLink(meshCreate.camera, meshRenderer.camera)
                        self.network.addLink(meshRenderer.camera, meshCreate.camera)
                        meshCreate.meshType.selectedIndex = 13
                        meshCreate.scale.value = radius/30
                        meshCreate.color.value = inviwopy.glm.vec4(color[0],color[1],color[2],0.7)
                        meshCreate.position1.value = inviwopy.glm.vec3(n[0]-0.5, n[1]-0.5, n[2]-0.5)

        self.decoration_outport = vectorRenderer.getOutport('image')
        self.decoration_inport = vectorRenderer.getInport('imageInport')
        self.camera_prop = vectorRenderer.camera


#Filer att skriva i:
# -VisualisationManager (klart)
# - EnvisionMain (kanske)

import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from envisionpy.utils.atomData import atomic_radii, element_names, element_colors
from .baseNetworks.Decoration import Decoration

class MolecularDynamics(Decoration):
    '''
    Manages a subnetwork for animation of molecular dynamics.

    *insert utförligare beskrivning here*
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_output, xpos=0, ypos=0):
        Decoration.__init__(self,inviwoApp)
        self.atom_radii = []
        self.atom_names = []
        self.nAtomTypes = 0
        self.setup_network(hdf5_path, hdf5_output, xpos, ypos)

        #self.set_atom_radius(0.5)
        self.toggle_full_mesh(True)
        self.hide()

    @staticmethod
    def valid_hdf5(hdf5_file):
        #Test if the MD-section of the hdf5 file is empty.
        #Returns True if the MD-section of the hdf5 file is not empty.
            return hdf5_file.get("MD") != None        #Kolla närmare på formatet för HDF5-filer. Detta verkar orsaka problem

    def get_ui_data(self):
        #Return a list of data to show on the user interface.
        return [
            self.atom_names,
            self.atom_radii
        ]

    def valid_visualisations(self):         #Osäker på funktionaliteten kring denna funktion, behövs den?
        #Return a list of valid decorations.
        return ['charge', 'elf', 'parchg']

    def connect_decoration(self, other, vis_type):
        # Connect properties and ports between visualisations.
        if vis_type not in self.valid_decorations():
            raise EnvisionError('Invalid decoration type ['+vis_type+'].')

        self.other_subnetworks[vis_type] = otherwise

        #Link needed properties between networks.
        if vis_type == 'molecular_dynamics':                        #ändra till md??
            self.network.addLink(other.camera_prop, self.camera_prop)
            self.network.addLink(self.camera_prop, other.camera_prop)
            other.camera_prop.invalidate()

        other.connect_decoration_ports(self.decoration_outport)

    def disconnect_decoration(self, other, vis_type):
        # Disconnect properties and ports between visualisations.
        if vis_type == 'molecular_dynamics':                           #samma här
            self.network.removeLink(self.camera_prop, other.camera_prop)
        other.disconnect_decorations_port(self.decoration_outport)

    def show(self):
        self.get_processor('UnitcellCanvas').widget.show()

    def hide(self):
        self.get_processor('UnitcellCanvas').widget.hide()

# ------------------------------------------
# ------- Property control functions -------

#Om vi inte kallar på denna function, behövs den då?
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
        #Uppdates the position of the canvas
        #Upper left corner will be at coordinate (x,y)
            unitcellCanvas = self.get_processor('UnitcellMesh')
            unitcellCanvas.position.value = inviwopy.glm.ivec2(x, y)

# ------------------------------------------
# ------- Network building functions -------

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        # Set up the processor network for this visualistion.
        strucMesh = self.add_processor('envision.StructureMesh', 'UnitcellMesh', xpos, ypos+3)
        meshRender = self.add_processor('org.inviwo.SphereRenderer', 'UnitcellRenderer', xpos, ypos+6)
        background = self.add_processor('org.inviwo.Background', 'AtomBackground', xpos, ypos+9)
        canvas = self.add_processor('org.inviwo.CanvasGL', 'UnitcellCanvas', xpos, ypos+12)
        propertyAnimator = self.add_processor('org.inviwo.OrdinalPropertyAnimator', 'Animator', xpos+7, ypos+3) #Vet ej om notationen är rätt

        canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)

        self.network.addConnection(strucMesh.getOutport('mesh'), meshRender.getInport('geometry'))
        self.network.addConnection(meshRender.getOutport('image'), background.getInport('inport'))
        self.network.addConnection(background.getOutport('outport'), canvas.getInport('inport'))

        with h5py.File(hdf5_path, "r") as h5:
            # Set basis matrix and scaling
                                                #Osäker på vad detta gör och om det behövs?
            strucMesh.basis.value = inviwopy.glm.mat3(
                1, 0, 0,
                0, 1, 0,
                0, 0, 1)

            #base_group = "/UnitCell"
            MD_group = "/MD"
            # -----------TEMPORÄRT UTANFÖR LOOPEN PÅ RAD 139 --------------
            coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(0,"Fe"), xpos-1*7, ypos)
            self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
            self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))

            for i, key in enumerate(list(h5[MD_group + "/Atoms"].keys())):  #Hur ser hdf5-filen ut nu igen?
                # element = h5[MD_group + "/Atoms/"+key].attrs['element']
                # name = element_names.get(element, 'Unknown')
                # color = element_colors.get(element, (0.5, 0.5, 0.5, 0.5))
                # radius = atomic_radii.get(element, 0.5)
                # self.atom_names.append(name)
                # self.atom_radii.append(radius)


                #Ersätt sträng i coordReader till variablen name när giltig name finns.
                #coordReader = self.add_processor('envision.CoordinateReader', '{0} {1}'.format(i,"Fe"), xpos-i*7, ypos)
                # self.network.addConnection(hdf5_output, coordReader.getInport('inport'))
                # self.network.addConnection(coordReader.getOutport('outport'), strucMesh.getInport('coordinates'))
                #self.network.addLink(propertyAnimator.getOutport('outport'), coordReader.getInport('inport'))
                #self.network.addConnection(propertyAnimator.getOutport('outport'), coordReader.getInport('inport'))
                coordReader.path.value = MD_group + '/Atoms/' + key
                #Koppla property_animator till CoordinateReader!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                                                                            #Osäker på vad fan detta block gör för något
                # if strucMesh.getPropertyByIdentifier('radius{0}'.format(i)) == None:
                #         continue
                # strucMesh_radius_property = strucMesh.getPropertyByIdentifier('radius{0}'.format(i))
                # strucMesh_radius_property.maxValue = 10
                # strucMesh_radius_property.minValue = 0.001
                # strucMesh_radius_property.value = 0.5
                #
                # strucMesh_color_property = strucMesh.getPropertyByIdentifier('color{0}'.format(i))
                # strucMesh_color_property.value = inviwopy.glm.vec4(color[0],color[1],color[2],color[3])
                #
                # strucMesh_atom_property = strucMesh.getPropertyByIdentifier('atoms{0}'.format(i))
                # print('atoms{0}'.format(i))
                # strucMesh_atom_property.value = 0
                # strucMesh_atom_property.minValue = 0
                # strucMesh_atom_property.maxValue = 0

                self.nAtomTypes += 1


        self.decoration_outport = meshRender.getOutport('image')
        self.decoration_inport = meshRender.getInport('imageInport')
        self.camera_prop = meshRender.camera

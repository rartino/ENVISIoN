#  Created by Jesper Ericsson
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
import h5py


from .LinePlotNetworkHandler import LinePlotNetworkHandler

class BandstructureNetworkHandler(LinePlotNetworkHandler):
    """ Handler class for charge visualization network.
        Sets up and manages the charge visualization
    """
    def __init__(self, hdf5_path, inviwoApp):
        LinePlotNetworkHandler.__init__(self, inviwoApp)
        self.setup_bandstructure_network(hdf5_path)

# ------------------------------------------
# ------- Network building functions -------

    def setup_bandstructure_network(self, hdf5_path, xpos=0, ypos=0):
        with h5py.File(hdf5_path,"r") as h5:
            # A bool that tells if the band structure should be normalized around the fermi energy.
            has_fermi_energy = "/FermiEnergy" in h5

            # Start building the Inviwo network.
            h5source = self.add_h5source(hdf5_path, xpos, ypos)
            ypos += 75

            path_selection = self.add_processor("org.inviwo.hdf5.PathSelection", "Select Bandstructure", xpos, ypos)
            self.network.addConnection(h5source.getOutport("outport"),
                                  path_selection.getInport("inport"))

            if has_fermi_energy:
                fermi_point = self.add_processor("org.inviwo.HDF5ToPoint", "Fermi energy", xpos + 175, ypos)
                self.network.addConnection(h5source.getOutport("outport"),
                                    fermi_point.getInport("hdf5HandleFlatMultiInport"))

            ypos += 75

            all_children_processor = self.add_processor("org.inviwo.HDF5PathSelectionAllChildren", "Select all bands", xpos, ypos)
            self.network.addConnection(path_selection.getOutport("outport"),
                                all_children_processor.getInport("hdf5HandleInport"))
            ypos += 75

            HDF5_to_function = self.add_processor("org.inviwo.HDF5ToFunction", "Convert to function", xpos, ypos)
            self.network.addConnection(all_children_processor.getOutport("hdf5HandleVectorOutport"),
                                HDF5_to_function.getInport("hdf5HandleFlatMultiInport"))
            ypos += 75

            function_to_dataframe = self.get_processor("Function to dataframe")
            self.network.addConnection(HDF5_to_function.getOutport("functionVectorOutport"),
                                        function_to_dataframe.getInport("functionFlatMultiInport"))
                                        
            if has_fermi_energy:
                self.network.addConnection(fermi_point.getOutport("pointVectorOutport"),
                                    self.get_processor("Line plot").getInport("pointInport"))

            
            if has_fermi_energy:
                self.set_title("Energy - Fermi energy  [eV]")
            else:
                self.set_title("Energy [eV]")
            # energy_text_processor.font.fontSize.value = 20
            # energy_text_processor.position.value = inviwopy.glm.vec2(0.31, 0.93)
            # energy_text_processor.color.value = inviwopy.glm.vec4(0,0,0,1)

            # Start modifying properties.
            path_selection.selection.value = '/Bandstructure/Bands'
            # HDF5_to_function.yPathSelectionProperty.value = '/Energy'
            self.toggle_all_y(True)
            # background_processor.bgColor1.value = inviwopy.glm.vec4(1)
            # background_processor.bgColor2.value = inviwopy.glm.vec4(1)
            # canvas_processor.inputSize.dimensions.value = inviwopy.glm.ivec2(900, 700)
            if has_fermi_energy:
                fermi_point.pathSelectionProperty.value = '/FermiEnergy'

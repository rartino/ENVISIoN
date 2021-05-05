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

# TODO: add hdf5 validation

import sys,os,inspect

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

    def get_ui_data(self):
    # Return data required to fill user interface
        return [
            "bandstructure",
            LinePlotNetworkHandler.get_ui_data(self)
            ]

    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("BandStructure") != None
        

    def stop_vis(self, vis_type = None):
        print('Stopping 2d')
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

            # if has_fermi_energy:
            #     fermi_point = self.add_processor("org.inviwo.HDF5ToPoint", "Fermi energy", xpos + 175, ypos)
            #     self.network.addConnection(h5source.getOutport("outport"),
            #                         fermi_point.getInport("hdf5HandleFlatMultiInport"))

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

            # if has_fermi_energy:
            #     self.network.addConnection(fermi_point.getOutport("pointVectorOutport"),
            #                         self.get_processor("Line plot").getInport("pointInport"))


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
            # self.toggle_all_y(True)
            self.set_y_selection_type(2)
            # background_processor.bgColor1.value = inviwopy.glm.vec4(1)
            # background_processor.bgColor2.value = inviwopy.glm.vec4(1)
            # canvas_processor.inputSize.dimensions.value = inviwopy.glm.ivec2(900, 700)
            # if has_fermi_energy:
            #     fermi_point.pathSelectionProperty.value = '/FermiEnergy'

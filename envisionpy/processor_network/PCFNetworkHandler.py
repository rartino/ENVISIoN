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


import sys,os,inspect
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py


from .LinePlotNetworkHandler import LinePlotNetworkHandler

class PCFNetworkHandler(LinePlotNetworkHandler):
    """ Handler class for charge visualization network.
        Sets up and manages the charge visualization
    """
    def __init__(self, hdf5_path, inviwoApp):
        LinePlotNetworkHandler.__init__(self, inviwoApp)
        self.setup_PCF_network(hdf5_path)

    def get_ui_data(self):
    # Return data required to fill user interface
        return [
            "pcf",
            LinePlotNetworkHandler.get_ui_data(self)
            ]

    @staticmethod
    def valid_hdf5(hdf5_file):
        return True
# ------------------------------------------
# ------- Network building functions -------

    def setup_PCF_network(self, hdf5_path, xpos=0, ypos=0):
        # Creates inviwo self.network for the pair correlation function, PCF for short.
        with h5py.File(hdf5_path, "r") as h5:
            #Create HDF5_to_func_list
            HDF5_to_func_list = []
            element_in_system_list = []

            #PCF can be parsed to two structures. See what kind of HDF5-structure is present.
            h5source = self.add_h5source(hdf5_path, xpos, ypos)
            ypos += 75

            path_selection = self.add_processor("org.inviwo.hdf5.PathSelection", "Select Paircorrelation", xpos, ypos)
            self.network.addConnection(h5source.getOutport("outport"), path_selection.getInport("inport"))

            ypos += 150
            function_to_dataframe = self.get_processor("Function to dataframe")

            ypos_tmp = ypos-75
            xpos_tmp = xpos

            # is_h5_onecol is True when _write_pcdat_onecol has been used for PCF parsning.
            is_h5_onecol = False
            #How many timeframes in structure when _write_pcdat_onecol is used?
            if "Elements" in h5["PairCorrelationFunc"]:
                is_h5_onecol = True
                #Go through all timeframes for all Elements.
                for element_count in range(len(h5["PairCorrelationFunc/Elements"])):
                    elements_in_system = list(h5["PairCorrelationFunc/Elements"].keys())[element_count]
                    element_in_system_list.append(elements_in_system)

                    path_str = "PairCorrelationFunc/Elements/" + elements_in_system
                    for t_values in range(len(h5[path_str])):
                        xpos_tmp += 165
                        HDF5_to_func = self.add_processor("org.inviwo.HDF5ToFunction", "HDF5 To Function", xpos_tmp, ypos_tmp)
                        self.network.addConnection(path_selection.getOutport("outport"), HDF5_to_func.getInport("hdf5HandleFlatMultiInport"))
                        self.network.addConnection(HDF5_to_func.getOutport("functionVectorOutport"), function_to_dataframe.getInport("functionFlatMultiInport"))
                        HDF5_to_func_list.append(HDF5_to_func)
            else:
                for t_values in range(len(h5["PairCorrelationFunc"]) - 1):
                    xpos_tmp += 165
                    HDF5_to_func = self.add_processor("org.inviwo.HDF5ToFunction", "HDF5 To Function", xpos_tmp, ypos_tmp)
                    self.network.addConnection(path_selection.getOutport("outport"), HDF5_to_func.getInport("hdf5HandleFlatMultiInport"))
                    self.network.addConnection(HDF5_to_func.getOutport("functionVectorOutport"),
                                        function_to_dataframe.getInport("functionFlatMultiInport"))
                    HDF5_to_func_list.append(HDF5_to_func)


            #for t_values in range():
            #ypos += 75
            #HDF5_to_func_processor = self.add_processor("org.inviwo.HDF5ToFunction", "To Function", xpos, ypos)
            #network.addConnection(paircorrelation_processor.getOutport("outport"), HDF5_to_func_processor.getInport("hdf5HandleFlatMultiInport"))

            self.network.addConnection(HDF5_to_func.getOutport("functionVectorOutport"), function_to_dataframe.getInport("functionFlatMultiInport"))

            # Set processor properties
            path_selection.selection.value = "/PairCorrelationFunc"
            #

            # if Elements are in h5, parsing is using _write_pcdat_multicol else _write_pcdat_onecol is used.
            for processor_count in range(len(HDF5_to_func_list)):
                h5_from_list = HDF5_to_func_list[processor_count]

                if is_h5_onecol:
                    h5_from_list.implicitXProperty.value = False
                    h5_from_list.xPathSelectionProperty.value = "/Distance"
                    for chosen_element in element_in_system_list:
                        h5_from_list.yPathSelectionProperty.value = "/Elements/" + chosen_element + "/PCF for t_" + str(processor_count)
                else:
                    h5_from_list.implicitXProperty.value = False
                    h5_from_list.xPathSelectionProperty.value = "/Distance"
                    h5_from_list.yPathSelectionProperty.value = "/PCF for t_" + str(processor_count)




            #Default settings, first value chosen. Different graphs can later be chosen by GUI through Line Plot Processor
            if is_h5_onecol:
                first_element = list(h5["PairCorrelationFunc/Elements"].keys())[0]
                HDF5_to_func.yPathSelectionProperty.value = "/Elements/" + first_element + "/PCF for t_0"

            else:
                HDF5_to_func.yPathSelectionProperty.value = "/PCF for t_0"


            self.set_y_single_selection_string("PCF for t_0")
            self.set_title("Pair Correlation Function")


            # Default setting of background and title
            # background_processor.bgColor1.value = inviwopy.glm.vec4(1)
            # background_processor.backgroundStyle = "Uniform color"
            # text_overlay_processor.color.value = inviwopy.glm.vec4(0, 0, 0, 1)
            # text_overlay_processor.position.value = inviwopy.glm.vec2(0.34, 0.86)
            # text_overlay_processor.font.fontSize.value = 22
            # text_overlay_processor.font.fontFace.value = "OpenSans Bold"

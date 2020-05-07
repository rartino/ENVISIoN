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


from .NetworkHandler import NetworkHandler
from envisionpy.utils.exceptions import *

class LinePlotNetworkHandler(NetworkHandler):
    """ Handler class for charge visualization network.
        Sets up and manages the charge visualization
    """
    def __init__(self, inviwoApp):
        NetworkHandler.__init__(self, inviwoApp)
        self.setup_plot_network()


    def get_ui_data(self):
        return [
            "lineplot",
            self.get_x_range(),
            self.get_y_range(),
            self.get_line_enabled(),
            self.get_line_x(),
            self.get_grid_enabled(),
            self.get_grid_width(),
            self.get_x_labels_enabled(),
            self.get_y_labels_enabled(),
            self.get_label_n(),
            self.get_y_selection_info(),
            self.get_available_datasets()
        ]
# ------------------------------------------
# ------- Property functions -------


    def toggle_graph_canvas(self, enable):
    # Will add or remove the slice canvas
        try:
            graphCanvas = self.get_processor('graphCanvas')
        except ProcessorNotFoundError:
            graphCanvas = None
        
        # If already in correct mode dont do anything
        if (graphCanvas and enable) or (not graphCanvas and not enable):
            return

        if enable:
            graphCanvas = self.add_processor('org.inviwo.CanvasGL', 'graphCanvas', 25*7, 525)
            graphCanvas.inputSize.dimensions.value = inviwopy.glm.ivec2(500, 500)       
            self.network.addConnection(self.get_processor("Title text").getOutport('outport'), graphCanvas.getInport('inport'))
        else:
            self.remove_processor('graphCanvas')

    def set_y_selection_type(self, option):
    # Set the type for date selection for Y datasets
    # 0: single dataset. 1: multiple datasets. 2: all datasets
        plotter = self.get_processor("Line plot")
        plotter.boolYSelection.value = (option == 1)
        plotter.allYSelection.value = (option == 2)

    def set_y_single_selection_index(self, index):
        plotter = self.get_processor("Line plot")
        plotter.ySelectionProperty.selectedIndex = index

    def set_y_single_selection_string(self, name):
        plotter = self.get_processor("Line plot")
        plotter.ySelectionProperty.value = name

    def set_y_multi_selection(self, selection):
        plotter = self.get_processor("Line plot")
        plotter.groupYSelection_.value = selection

    def set_title(self, title):
        title_text = self.get_processor("Title text")
        title_text.text.value = title

    def set_title_font(self):
        pass

    def set_title_font_size(self):
        pass

    def set_title_color(self):
        pass

    def set_x_range(self, xMax, xMin):
        plotter = self.get_processor("Line plot")
        plotter.x_range.value = inviwopy.glm.vec2(xMin, xMax)

    def set_y_range(self, xMax, xMin):
        plotter = self.get_processor("Line plot")
        plotter.y_range.value = inviwopy.glm.vec2(xMin, xMax)

    def toggle_vertical_line(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.enable_line.value = enable

    def set_vertical_line_x(self, xPos):
        plotter = self.get_processor("Line plot")
        plotter.line_x_coordinate.value = xPos

    def toggle_grid(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.enable_grid.value = enable
    
    def set_grid_size(self, width):
        plotter = self.get_processor("Line plot")
        plotter.grid_width.value = width

    def toggle_x_label(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.show_x_labels.value = enable

    def toggle_y_label(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.show_y_labels.value = enable
    def set_n_labels(self, n):
        plotter = self.get_processor("Line plot")
        plotter.label_number.value = n
    
    # ------------------------------------------------
    # -------- Value getting functions for UI --------
    # ------------------------------------------------
    def get_dataset_list(self):
        Plotter = self.get_processor("Line plot")
        return Plotter.ySelectionProperty.identifiers

    def get_x_range(self):
        value = self.get_processor("Line plot").x_range.value
        return [value[0], value[1]]

    def get_y_range(self):
        value = self.get_processor("Line plot").y_range.value
        return [value[0], value[1]]

    def get_line_enabled(self):
        return self.get_processor("Line plot").enable_line.value

    def get_line_x(self):
        return self.get_processor("Line plot").line_x_coordinate.value

    def get_grid_enabled(self):
        return self.get_processor("Line plot").enable_grid.value

    def get_grid_width(self):
        return self.get_processor("Line plot").grid_width.value

    def get_x_labels_enabled(self):
        return self.get_processor("Line plot").show_x_labels.value

    def get_y_labels_enabled(self):
        return self.get_processor("Line plot").show_y_labels.value
    
    def get_label_n(self):
        return self.get_processor("Line plot").label_number.value

    def get_y_selection_info(self):
        plotter = self.get_processor("Line plot")
        if plotter.allYSelection.value:
            return [2]
        if plotter.boolYSelection.value:
            return [1, plotter.groupYSelection_.value]
        return [0, plotter.ySelectionProperty.selectedIndex]

    def get_available_datasets(self):
        plotter = self.get_processor("Line plot")
        return plotter.xSelectionProperty.identifiers   
    # def get_grid_width(self):
    #     pass

    def get_label_count(self):
        return self.get_processor("Line plot").label_number.value


# ------------------------------------------
# ------- Network building functions -------

    def setup_plot_network(self, xpos=0, ypos=300):

        function_to_dataframe = self.add_processor("org.inviwo.FunctionToDataFrame", "Function to dataframe", xpos, ypos)
        # self.network.addConnection(HDF5_to_function_processor.getOutport("functionVectorOutport"),
        #                     function_to_dataframe_processor.getInport("functionFlatMultiInport"))
        ypos += 75

        line_plot = self.add_processor("org.inviwo.LinePlotProcessor", "Line plot", xpos, ypos)
        self.network.addConnection(function_to_dataframe.getOutport("dataframeOutport"),
                                   line_plot.getInport("dataFrameInport"))

        # if has_fermi_energy:
        #     self.network.addConnection(fermi_point_processor.getOutport("pointVectorOutport"),
        #                         line_plot_processor.getInport("pointInport"))

        ypos += 75

        mesh_renderer = self.add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Mesh renderer", xpos, ypos)
        self.network.addConnection(line_plot.getOutport("outport"),
                                   mesh_renderer.getInport("inputMesh"))
        self.network.addConnection(line_plot.getOutport("labels"),
                                   mesh_renderer.getInport("imageInport"))
        ypos += 75

        background = self.add_processor("org.inviwo.Background", "Background", xpos, ypos)
        self.network.addConnection(mesh_renderer.getOutport("outputImage"),
                            background.getInport("inport"))
        ypos += 75

        title_text = self.add_processor("org.inviwo.TextOverlayGL", "Title text", xpos, ypos)
        self.network.addConnection(background.getOutport('outport'), title_text.getInport('inport'))
        # if has_fermi_energy:
        #     energy_text_processor.text.value = 'Energy - Fermi energy  [eV]'
        # else:
        #     energy_text_processor.text.value = 'Energy [eV]'
        title_text.font.fontSize.value = 20
        # plotter_processor.font.anchor.value = inviwopy.glm.vec2(-1, -0.9234)
        title_text.position.value = inviwopy.glm.vec2(0.31, 0.93)
        title_text.color.value = inviwopy.glm.vec4(0,0,0,1)

        ypos += 75

        canvas = self.add_processor("org.inviwo.CanvasGL", "graphCanvas", xpos, ypos)
        self.network.addConnection(title_text.getOutport('outport'), canvas.getInport('inport'))
        
        # Start modifying properties.
        # path_selection_processor.selection.value = '/Bandstructure/Bands'
        # HDF5_to_function_processor.yPathSelectionProperty.value = '/Energy'
        # line_plot_processor.allYSelection.value = True
        background.bgColor1.value = inviwopy.glm.vec4(1)
        background.bgColor2.value = inviwopy.glm.vec4(1)
        canvas.inputSize.dimensions.value = inviwopy.glm.ivec2(900, 700)
        canvas.widget.show()

        # if has_fermi_energy:
        #     fermi_point_processor.pathSelectionProperty.value = '/FermiEnergy'

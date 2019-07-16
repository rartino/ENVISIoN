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
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py


from NetworkHandler import NetworkHandler

class LinePlotNetworkHandler(NetworkHandler):
    """ Handler class for charge visualization network.
        Sets up and manages the charge visualization
    """
    def __init__(self, inviwoApp):
        NetworkHandler.__init__(self, inviwoApp)
        self.setup_plot_network()

# ------------------------------------------
# ------- Property functions -------

    def toggle_all_y(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.allYSelection.value = enable
        return [True, None]

    def toggle_multiple_y(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.boolYSelection.value = enable
        return [True, None]

    def set_y_selection_type(self, option):
    # Set the type for date selection for Y datasets
    # 0: single dataset. 1: multiple datasets. 2: all datasets
        plotter = self.get_processor("Line plot")
        plotter.boolYSelection.value = (option == 1)
        plotter.allYSelection.value = (option == 2)
        return [True, None]


    
    def set_y_single_selection(self, index):
        plotter = self.get_processor("Line plot")
        plotter.ySelectionProperty.selectedIndex = index
        return [True, None]
    
    def set_y_multi_selection(self, selection):
        plotter = self.get_processor("Line plot")
        plotter.groupYSelection_.value = selection
        return [True, None]


    def get_available_datasets(self):
        plotter = self.get_processor("Line plot")
        return [True, plotter.xSelectionProperty.identifiers]




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
        return [True, None]

    def set_y_range(self, xMax, xMin):
        plotter = self.get_processor("Line plot")
        plotter.y_range.value = inviwopy.glm.vec2(xMin, xMax)
        return [True, None]

    def toggle_vertical_line(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.enable_line.value = enable
        return [True, None]

    def set_vertical_line_x(self, xPos):
        plotter = self.get_processor("Line plot")
        plotter.line_x_coordinate.value = xPos
        return [True, None]

    def toggle_grid(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.enable_grid.value = enable
        return [True, None]
    
    def set_grid_size(self, width):
        plotter = self.get_processor("Line plot")
        plotter.grid_width.value = width
        return [True, None]

    def toggle_x_label(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.show_x_labels.value = enable
        return [True, None]

    def toggle_y_label(self, enable):
        plotter = self.get_processor("Line plot")
        plotter.show_y_labels.value = enable
        return [True, None]

    def set_n_labels(self, n):
        plotter = self.get_processor("Line plot")
        plotter.label_number.value = n
        return [True, None]
    
    def get_dataset_list(self):
        Plotter = self.get_processor("Line plot")
        return [True, Plotter.ySelectionProperty.identifiers]
    
    

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

        canvas = self.add_processor("org.inviwo.CanvasGL", "Canvas", xpos, ypos)
        self.network.addConnection(title_text.getOutport('outport'), canvas.getInport('inport'))

        # Start modifying properties.
        # path_selection_processor.selection.value = '/Bandstructure/Bands'
        # HDF5_to_function_processor.yPathSelectionProperty.value = '/Energy'
        # line_plot_processor.allYSelection.value = True
        background.bgColor1.value = inviwopy.glm.vec4(1)
        background.bgColor2.value = inviwopy.glm.vec4(1)
        canvas.inputSize.dimensions.value = inviwopy.glm.ivec2(900, 700)
        # if has_fermi_energy:
        #     fermi_point_processor.pathSelectionProperty.value = '/FermiEnergy'

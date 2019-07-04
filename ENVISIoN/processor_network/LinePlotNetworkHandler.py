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
        plotter.allYSelection.value = True

    def set_y_selection(self, selection):
        plotter = self.get_processor("Line plot")
        plotter.ySelectionProperty.value = selection

    def set_title(self, title):
        title_text = self.get_processor("Title text")
        title_text.text.value = title

    def set_title_font(self):
        pass

    def set_title_font_size(self):
        pass

    def set_title_color(self):
        pass
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

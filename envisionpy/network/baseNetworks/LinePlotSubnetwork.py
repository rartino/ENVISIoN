import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork


class LinePlotSubnetwork(Subnetwork):
    '''
    Manages a subnetwork for generic volume rendering. 
    Used for charge density, ELF, and fermi surface visualisations.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0, multichannel=False):
        Subnetwork.__init__(self, inviwoApp)
        self.setup_network(hdf5_outport, xpos, ypos)

    def show(self):
        self.get_processor('Canvas').widget.show()
    def hide(self, hide_volume=True, hide_slice=True):
        self.get_processor('Canvas').widget.hide()

# ------------------------------------------
# ------- Property control functions -------

    def set_y_selection_type(self, option):
        # Set the type for date selection for Y datasets
        # 0: single dataset. 1: multiple datasets. 2: all datasets
        plotter = self.get_processor("LinePlot")
        plotter.boolYSelection.value = (option == 1)
        plotter.allYSelection.value = (option == 2)

    def set_y_single_selection_index(self, index):
        plotter = self.get_processor("LinePlot")
        plotter.ySelectionProperty.selectedIndex = index

    def set_y_single_selection_string(self, name):
        plotter = self.get_processor("LinePlot")
        plotter.ySelectionProperty.value = name

    def set_y_multi_selection(self, selection_string):
        plotter = self.get_processor("LinePlot")
        plotter.groupYSelection_.value = selection_string

    def set_title(self, title):
        self.get_processor("TitleText").value = title

    def set_x_range(self, xMax, xMin):
        plotter = self.get_processor("LinePlot")
        plotter.x_range.maxValue = inviwopy.glm.vec2(xMax, xMax)
        plotter.x_range.minValue = inviwopy.glm.vec2(xMin, xMin)
        plotter.x_range.value = inviwopy.glm.vec2(xMin, xMax)

    def set_y_range(self, yMax, yMin):
        plotter = self.get_processor("LinePlot")
        plotter.y_range.maxValue = inviwopy.glm.vec2(yMax, yMax)
        plotter.y_range.minValue = inviwopy.glm.vec2(yMin, yMin)
        plotter.y_range.value = inviwopy.glm.vec2(yMin, yMax)

    def toggle_vertical_line(self, enable):
        plotter = self.get_processor("LinePlot")
        plotter.enable_line.value = enable

    def set_vertical_line_x(self, xPos):
        plotter = self.get_processor("LinePlot")
        plotter.line_x_coordinate.maxValue = xPos + 10
        plotter.line_x_coordinate.minValue = xPos - 10
        plotter.line_x_coordinate.value = xPos

    def toggle_grid(self, enable):
        plotter = self.get_processor("LinePlot")
        plotter.enable_grid.value = enable
    
    def set_grid_size(self, width):
        plotter = self.get_processor("LinePlot")
        plotter.grid_width.value = width

    def toggle_x_label(self, enable):
        plotter = self.get_processor("LinePlot")
        plotter.show_x_labels.value = enable

    def toggle_y_label(self, enable):
        plotter = self.get_processor("LinePlot")
        plotter.show_y_labels.value = enable
        
    def set_n_labels(self, n):
        plotter = self.get_processor("LinePlot")
        plotter.label_number.value = n

# ------------------------------------------
# ------- Network building functions -------

    def set_hdf5_subpath(self, path):
        # vis = self.get_processor('Canvas').widget.visibility
        # self.hide()
        # self.show() 
        # self.show() if vis else self.hide() # Flashing canvas forces network update to refresh options.

        hdf5Path = self.get_processor('PathSelection')
        hdf5Path.selection.selectedValue = path


    def setup_network(self, hdf5_outport, xpos, ypos):

        pathSelection = self.add_processor("org.inviwo.hdf5.PathSelection", "PathSelection", xpos, ypos)
        self.network.addConnection(hdf5_outport, pathSelection.getInport("inport"))

        childCollector = self.add_processor("org.inviwo.HDF5PathSelectionAllChildren", "ChildCollector", xpos, ypos+3)
        self.network.addConnection(pathSelection.getOutport("outport"), childCollector.getInport("hdf5HandleInport"))

        toFunction = self.add_processor("org.inviwo.HDF5ToFunction", "h5ToFunction", xpos, ypos+6)
        self.network.addConnection(childCollector.getOutport("hdf5HandleVectorOutport"), toFunction.getInport("hdf5HandleFlatMultiInport"))

        dataFrame = self.add_processor("org.inviwo.FunctionToDataFrame", "dataFrame", xpos, ypos+9)
        self.network.addConnection(toFunction.getOutport("functionVectorOutport"), dataFrame.getInport("functionFlatMultiInport"))

        linePlot = self.add_processor("org.inviwo.LinePlotProcessor", "LinePlot", xpos, ypos+12)
        self.network.addConnection(dataFrame.getOutport("dataframeOutport"), linePlot.getInport("dataFrameInport"))

        meshRenderer = self.add_processor("org.inviwo.Mesh2DRenderProcessorGL", "MeshRenderer", xpos, ypos+15)
        self.network.addConnection(linePlot.getOutport("outport"),
                                   meshRenderer.getInport("inputMesh"))
        self.network.addConnection(linePlot.getOutport("labels"),
                                   meshRenderer.getInport("imageInport"))


        background = self.add_processor("org.inviwo.Background", "Background", xpos, ypos+18)
        self.network.addConnection(meshRenderer.getOutport("outputImage"),
                            background.getInport("inport"))

        titleText = self.add_processor("org.inviwo.TextOverlayGL", "TitleText", xpos, ypos+21)
        self.network.addConnection(background.getOutport('outport'), titleText.getInport('inport'))

        titleText.font.fontSize.value = 20
        titleText.position.value = inviwopy.glm.vec2(0.31, 0.93)
        titleText.color.value = inviwopy.glm.vec4(0,0,0,1)

        canvas = self.add_processor("org.inviwo.CanvasGL", "Canvas", xpos, ypos+24)
        self.network.addConnection(titleText.getOutport('outport'), canvas.getInport('inport'))

        # # Setup 3d view
        # meshCreator = self.add_processor('org.inviwo.MeshCreator', 'MeshCreator', xpos-14, ypos+12)
        # hfRender = self.add_processor('org.inviwo.HeightFieldRenderGL', 'HFRender', xpos-14, ypos+15)
        # self.network.addConnection(meshCreator.getOutport('outport'), hfRender.getInport('geometry'))
        # self.network.addConnection(titleText.getOutport('outport'), hfRender.getInport('texture'))

        background.bgColor1.value = inviwopy.glm.vec4(1)
        background.bgColor2.value = inviwopy.glm.vec4(1)
        canvas.inputSize.dimensions.value = inviwopy.glm.size2_t(900, 700)
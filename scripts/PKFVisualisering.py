
import inviwopy
import numpy as np
import h5py

import os, sys

# Configuration
PATH_TO_ENVISION=os.path.expanduser("/home/labb/ENVISIoN-gui-dev/envision")
PATH_TO_VASP_CALC=os.path.expanduser("/home/labb/VASP_files/Cu-DoS/Cu/1/10")
PATH_TO_HDF5=os.path.expanduser("/home/labb/ENVISIoN-gui-dev/HDF5/demo_PKFtesting2.hdf5")

sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION))

import envision
import envision.inviwo

from envision.inviwo.common import _add_processor, _add_h5source, _add_property
from envision.inviwo.data import atomic_radii, element_names, element_colors
#import envision.parser

envision.parser.vasp.charge(PATH_TO_HDF5, PATH_TO_VASP_CALC)
app = inviwopy.app
network = app.network

def PKFVisualTest(h5file, xpos=0, ypos=0):
    network.clear()
    with h5py.File(h5file,"r") as h5:

        hdf5_to_list = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)

        ypos += 75

        bandstructure_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bandstructure", xpos, ypos)

        network.addConnection(h5source_processor.getOutport("outport"), bandstructure_processor.getInport("inport"))

        ypos += 75

        bands_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bands", xpos, ypos)

        network.addConnection(bandstructure_processor.getOutport("outport"), bands_processor.getInport("inport"))

        ypos += 75

        all_processor = _add_processor("org.inviwo.HDF5PathSelectionAllChildren", "Select All", xpos, ypos)

        network.addConnection(bands_processor.getOutport("outport"), all_processor.getInport("hdf5HandleInport"))

        ypos += 75

        band_processor = _add_processor("org.inviwo.HDF5ToFunction", "To Function", xpos, ypos)

        hdf5_to_list.append(band_processor)

        network.addConnection(all_processor.getOutport("hdf5HandleVectorOutport"), band_processor.getInport(

            "hdf5HandleFlatMultiInport"))

        ypos += 7
        operation_processor = _add_processor("org.inviwo.FunctionOperationNary", "Function to plotter", xpos, ypos)

        network.addConnection(band_processor.getOutport("functionVectorOutport"), operation_processor.getInport(

            "functionFlatMultiInport"))

        ypos += 75

        plotter_processor = _add_processor("org.inviwo.lineplotprocessor", "Band Structure Plotter", xpos, ypos)

        network.addConnection(operation_processor.getOutport("dataframeOutport"), plotter_processor.getInport("dataFrameInport"))

        ypos += 75


        mesh_renderer = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Renderer", xpos, ypos)

        network.addConnection(plotter_processor.getOutport("outport"), mesh_renderer.getInport('inputMesh'))

        network.addConnection(plotter_processor.getOutport("labels"), mesh_renderer.getInport('imageInport'))

        ypos += 75

        background_processor = _add_processor("org.inviwo.Background", "Background", xpos, ypos)

        network.addConnection(mesh_renderer.getOutport('outputImage'), background_processor.getInport('inport'))

        ypos += 75

        energy_text_processor = _add_processor("org.inviwo.TextOverlayGL", "Energy Text", xpos, ypos)

        network.addConnection(background_processor.getOutport('outport'), energy_text_processor.getInport('inport'))

        ypos += 75

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "Band Structure Canvas", xpos, ypos)

        network.addConnection(energy_text_processor.getOutport('outport'), canvas_processor.getInport("inport"))

        bandstructure_processor.getPropertyByIdentifier('selection').value = '/Bandstructure'

        bands_processor.getPropertyByIdentifier('selection').value = '/Bands'

        for hdf5_to in hdf5_to_list:

            hdf5_to.getPropertyByIdentifier('implicitXProperty').value = True

            hdf5_to.getPropertyByIdentifier('xPathSelectionProperty').value = '/n/Energy'

            hdf5_to.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(hdf5_to.identifier.split(' ')[0])

        operation_processor.getPropertyByIdentifier('operationProperty').value = 'add'

        background_processor.getPropertyByIdentifier('bgColor1').value = inviwopy.glm.vec4(1, 1, 1, 1)

        background_processor.getPropertyByIdentifier('bgColor2').value = inviwopy.glm.vec4(1, 1, 1, 1)

        energy_text_processor.getPropertyByIdentifier('text').value = 'Energy [eV]'

        energy_text_processor.getPropertyByIdentifier('position').value = inviwopy.glm.vec2(0.82, 0.03)

        energy_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0, 0, 0, 1)

        canvas_processor.getPropertyByIdentifier('inputSize').getPropertyByIdentifier(

            'dimensions').value = inviwopy.glm.ivec2(640, 480)

        plotter_processor.getPropertyByIdentifier("x_range").value = inviwopy.glm.vec2(1000, 0)




PKFVisualTest(PATH_TO_HDF5, xpos=0)



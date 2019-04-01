# Function to build an inviwo network for Radial distribution function.
import inviwopy
import numpy as np
import h5py
from .common import _add_h5source, _add_processor


app = inviwopy.app
network = app.netwrok

def paircorrelation(h5file, xstart_pos=0, ystart_pos=0):


# Creates inviwo nätverk för radial distribution function

    with h5py.File(h5file, "r") as h5:
        hdf5_to_test = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 75


    paircorrelation_function_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select paircorrelation_function", xpos, ypos)
    network.addConnection(h5source_processor.getOutport("outport"),
    Radial_distribution_Function_processor.getInport("inport"))
    ypos += 75

    Atoms_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Atoms", xpos, ypos)
    network.addConnection(paircorrelation_function()_processor.getOutport("outport"), Atoms_processor.getInport("inport"))
    ypos += 75

    All_processor = _add_processor("org.inviwo.hdf5.PathSelectionAllChildren", "Select All", xpos, ypos)
    network.addConnection(Atoms_processor.getOutport("outport"), all_processor.getInport("hdf5HandleInport"))
    ypos += 75

    Atom_processor = _add_processor("org.inviwo.HDF5ToFunction", "To Function", xpos, ypos)
    hdf5_to_list.append(Radial_processor)
    network.addConnection(all_processor.getOutport("hdf5HandleVectorOutport"), Atom_processor.getInport
    ("hdf5HandleFlastMultiInport"))
    ypos += 75

    operation_processor = _add_processor("org.inviwo.FunctionOperationNary", "Function to plotter", xpos, ypos)
    network.addConnection(operation_processor.getOutport("functionVectorOutport"), operation_processor.getInport
    ("functionFlatMultiInport"))
    ypos += 75

    plotter_processor = _add_processor("org.inviwo.lineplotprocessor", "paircorrelation plotter", xpos, ypos)
    network.addConnection(operation_processor.getOutport("dataframeOutport"), plotter_processor.getInport
    ("dataFrameInport"))
    y += 75

    mesh_renderer = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Renderer", xpos, ypos)
    network.addConnection(plotter_processor.getOutport("outport"), mesh_renderer.getInport('inputMesh'))
    network.addConnection(plotter_processor.getOutport("labels"), mesh_renderer.getInport('iamgeInport'))
    y += 75

    background_proceesor = _add_processor("org.inviwo.Background", "Distribution Text", xpos, ypos)
    network.addConnection(mesh_renderer.getOutport('outport'), distribution_text_processor.getInport('inport'))
    ypos += 75

    distribution_text_processor = _add_processor("org.inviwo.TextOverLayGL", "Energy Text", xpos, ypos)
    network.addConnection(background_proceesor.getOutport('outport'), energy_text_processor.getInport('inport'))
    ypos += 75

    canvas_processor = _add_processor("org.inviwo.CanvasGL", "paircorrelation Canvas", xpos, ypos)
    network.addConnection(distribution_text_processor.getOutport('outport'), canvas_processor.getInport("inport"))

    Radial_Func_processor.getPropertyByIdentifier('selection').value = '/paircorrelation'
    Atoms_processor.getPropertyByIdentifier('selection').value = '/Atoms'

    for hdf5_to in hdf5_to_list:
        hdf5_to.getPropertyByIdentifier('implicitXProperty').value = True
        hdf5_to.getPropertyByIdentifier('xPathSelectionProperty').value = '/n/Distribution'
        hdf5_to.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(hdf5_to.identifier.split(' ')[0])

    operation_processor.getPropertyByIdentifier('operationProperty').value = 'add'
    background_proceesor.getPropertyByIdentifier('bgColor').value = inviwopy.glm.vec4(1, 1, 1, 1)
    background_proceesor.getPropertyByIdentifier('bgColor2').value = inviwopy.glm.vec4(1, 1, 1, 1)
    distribution_text_processor.getPropertyByIdentifier('text').value = 'Distribution'
    distribution_text_processor.getPropertyByIdentifier('position').value = iviwopy.glm.vec2(0.82, 0.03)
    distribution_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0, 0, 0, 1)
    canvas_processor.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimension').value = \
        inviwopy.glm.ivec2(640, 480)
    plotter_processor.getPropertyByIdentifier("x_range").value = inviwopy.glm.vec2(1000, 0)

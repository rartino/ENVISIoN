# Function to build an inviwo network for Radial distribution function.
import inviwopy
import numpy as np
import h5py
from .common import _add_h5source, _add_processor


app = inviwopy.app
network = app.netwrok

def paircorrelation(h5file, xpos=0, ypos=0):


# Creates inviwo nätverk för radial distribution function

    with h5py.File(h5file, "r") as h5:
        hdf5_to_test = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 75


def bandstructure(h5file, xpos=0, ypos=0):
    """Creates an Inviwo network for band structure visualization

    This function will use a suitable HDF5 source processor if one is
    already present, otherwise one will be created. Likewise, a Fermi
    energy 2D graph marker processor will be reused or created
    as is needed.

    Parameters
    ----------
    h5file : str
        Path to HDF5 file
    xpos : int
         (Default value = 0)
         X coordinate in Inviwo network editor
    ypos : int
         (Default value = 0)
         Y coordinate in Inviwo network editor

     """

    with h5py.File(h5file, "r") as h5:
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
        ypos += 75

        """
        has_fermi_energy = "/FermiEnergy" in h5
        if has_fermi_energy:
            fermi_energy_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
            network.addConnection(h5source_processor.getOutport("outport"), fermi_energy_processor.getInport(
            "hdf5HandleFlatMultiInport"))
            ypos += 100
        """

        operation_processor = _add_processor("org.inviwo.FunctionOperationNary", "Function to plotter", xpos, ypos)
        network.addConnection(band_processor.getOutport("functionVectorOutport"), operation_processor.getInport(
            "functionFlatMultiInport"))
        ypos += 75

        plotter_processor = _add_processor("org.inviwo.lineplotprocessor", "Band Structure Plotter", xpos, ypos)
        network.addConnection(operation_processor.getOutport("dataframeOutport"),
                              plotter_processor.getInport("dataFrameInport"))
        ypos += 75

        """
        if has_fermi_energy:
            network.addConnection(fermi_energy_processor.getOutport("pointVectorOutport"), plotter_processor.getInport(
                "markYFlatMultiInport"))
            network.setPropertyValue(".".join([fermi_energy_processor, "pathSelectionProperty"]), "/{}".format("FermiEnergy"))
            network.setPropertyValue(".".join([fermi_energy_processor, "pathFreeze"]), True)

        network.setPropertyValue(".".join([plotter_processor, "markShiftToZeroYProperty"]), "Fermi Energy")
        """

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
            hdf5_to.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(
                hdf5_to.identifier.split(' ')[0])
        operation_processor.getPropertyByIdentifier('operationProperty').value = 'add'
        background_processor.getPropertyByIdentifier('bgColor1').value = inviwopy.glm.vec4(1, 1, 1, 1)
        background_processor.getPropertyByIdentifier('bgColor2').value = inviwopy.glm.vec4(1, 1, 1, 1)
        energy_text_processor.getPropertyByIdentifier('text').value = 'Energy [eV]'
        energy_text_processor.getPropertyByIdentifier('position').value = inviwopy.glm.vec2(0.82, 0.03)
        energy_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0, 0, 0, 1)
        canvas_processor.getPropertyByIdentifier('inputSize').getPropertyByIdentifier(
            'dimensions').value = inviwopy.glm.ivec2(640, 480)
        plotter_processor.getPropertyByIdentifier("x_range").value = inviwopy.glm.vec2(1000, 0)

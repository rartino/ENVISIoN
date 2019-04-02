#
#  ENVISIoN
#
#  Copyright (c) 2017 Robert Cranston
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

import inviwopy
import numpy as np
import h5py
from .common import _add_h5source, _add_processor

app = inviwopy.app
network = app.network

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

    with h5py.File(h5file,"r") as h5:
        hdf5_to_list = []
        operation_list = []
        plotter_list = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 75

        bandstructure_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bandstructure", xpos, ypos)
        network.addConnection(h5source_processor.getOutport("outport"), bandstructure_processor.getInport("inport"))
        ypos += 75

        mesh_renderer = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Renderer", xpos, ypos + 225)

        ypos_temp = ypos
        xpos_temp = xpos - 175
        for i in list(h5['Bandstructure/Bands'].keys()):
            ypos_temp = ypos
            xpos_temp = xpos_temp + 175
            band_processor = _add_processor("org.inviwo.HDF5ToFunction", "To Function " + i, xpos_temp, ypos_temp)
            hdf5_to_list.append(band_processor)
            network.addConnection(bandstructure_processor.getOutport("outport"), band_processor.getInport("hdf5HandleFlatMultiInport"))
            ypos_temp += 75

            """
            has_fermi_energy = "/FermiEnergy" in h5
            if has_fermi_energy:
                fermi_energy_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
                network.addConnection(h5source_processor.getOutport("outport"), fermi_energy_processor.getInport(
                "hdf5HandleFlatMultiInport"))
                ypos += 100
            """

            operation_processor = _add_processor("org.inviwo.FunctionOperationNary", "Function to plotter " + i, xpos_temp, ypos_temp)
            operation_list.append(operation_processor)
            network.addConnection(band_processor.getOutport("functionVectorOutport"), operation_processor.getInport(
                "functionFlatMultiInport"))
            ypos_temp += 75

            plotter_processor = _add_processor("org.inviwo.lineplotprocessor", "Band Structure Plotter " + i, xpos_temp, ypos_temp)
            plotter_list.append(plotter_processor)
            network.addConnection(operation_processor.getOutport("dataframeOutport"), plotter_processor.getInport("dataFrameInport"))
            ypos_temp += 75

            network.addConnection(plotter_processor.getOutport("outport"), mesh_renderer.getInport('inputMesh'))

        for plotter in plotter_list[1:]:
            network.addLink(plotter_list[0].scale, plotter.scale)
            network.addLink(plotter_list[0].x_range, plotter.x_range)
            network.addLink(plotter_list[0].y_range, plotter.y_range)

        network.addConnection(plotter_list[0].getOutport("labels"), mesh_renderer.getInport('imageInport'))

        ypos += 4 * 75

        """
        if has_fermi_energy:
            network.addConnection(fermi_energy_processor.getOutport("pointVectorOutport"), plotter_processor.getInport(
                "markYFlatMultiInport"))
            network.setPropertyValue(".".join([fermi_energy_processor, "pathSelectionProperty"]), "/{}".format("FermiEnergy"))
            network.setPropertyValue(".".join([fermi_energy_processor, "pathFreeze"]), True)

        network.setPropertyValue(".".join([plotter_processor, "markShiftToZeroYProperty"]), "Fermi Energy")
        """

        background_processor = _add_processor("org.inviwo.Background", "Background", xpos, ypos)
        network.addConnection(mesh_renderer.getOutport('outputImage'), background_processor.getInport('inport'))
        ypos += 75

        energy_text_processor = _add_processor("org.inviwo.TextOverlayGL", "Energy Text", xpos, ypos)
        network.addConnection(background_processor.getOutport('outport'), energy_text_processor.getInport('inport'))
        ypos += 75

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "Band Structure Canvas", xpos, ypos)
        network.addConnection(energy_text_processor.getOutport('outport'), canvas_processor.getInport("inport"))

        bandstructure_processor.getPropertyByIdentifier('selection').value = '/Bandstructure/Bands'
        for i in range(len(hdf5_to_list)):
            hdf5_to_list[i].getPropertyByIdentifier('implicitXProperty').value = True
            #hdf5_to.getPropertyByIdentifier('xPathSelectionProperty').value = '/n/Energy'
            hdf5_to_list[i].getPropertyByIdentifier('yPathSelectionProperty').value = '/{}/Energy'.format(str(i))
        operation_processor.getPropertyByIdentifier('operationProperty').value = 'add'
        background_processor.getPropertyByIdentifier('bgColor1').value = inviwopy.glm.vec4(1, 1, 1, 1)
        background_processor.getPropertyByIdentifier('bgColor2').value = inviwopy.glm.vec4(1, 1, 1, 1)
        energy_text_processor.getPropertyByIdentifier('text').value = 'Energy [eV]'
        energy_text_processor.getPropertyByIdentifier('position').value = inviwopy.glm.vec2(0.82, 0.03)
        energy_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0, 0, 0, 1)
        canvas_processor.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimensions').value = inviwopy.glm.ivec2(640, 480)
        #plotter_processor.getPropertyByIdentifier("x_range").value = inviwopy.glm.vec2(1000, 0)
        #plotter_processor.getPropertyByIdentifier("y_range").value = inviwopy.glm.vec2(1000, -1000)
        for plotter in plotter_list:
            print(plotter.y_range.value)



#  ENVISIoN
#
#  Copyright (c) 2019 Lloyd Kizito, Linda Le
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
#
#  Alterations to this file by Linda Le
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
import inviwopy
import numpy as np
import h5py
import math
from .common import _add_h5source, _add_processor

app = inviwopy.app
network = app.network


def paircorrelation(h5file, xpos=0, ypos=0):
    # Creates inviwo network for the pair correlation function, PCF for short.
    network.clear()

    with h5py.File(h5file, "r") as h5:
        #PCF can be parsed to two structures. See what kind of HDF5-structure is present.

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 75

        paircorrelation_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Paircorrelation", xpos, ypos)

        network.addConnection(h5source_processor.getOutport("outport"), paircorrelation_processor.getInport("inport"))

        ypos += 75

        HDF5_to_func_processor = _add_processor("org.inviwo.HDF5ToFunction", "To Function", xpos, ypos)
        network.addConnection(paircorrelation_processor.getOutport("outport"), HDF5_to_func_processor.getInport("hdf5HandleFlatMultiInport"))

        ypos += 75

        operation_processor = _add_processor("org.inviwo.FunctionOperationNary", "Function to plotter", xpos, ypos)
        network.addConnection(HDF5_to_func_processor.getOutport("functionVectorOutport"), operation_processor.getInport("functionFlatMultiInport"))
        ypos += 75

        plotter_processor = _add_processor("org.inviwo.LinePlotProcessor", "pair correlation plotter", xpos, ypos)
        network.addConnection(operation_processor.getOutport("dataframeOutport"), plotter_processor.getInport("dataFrameInport"))
        ypos += 75

        mesh_renderer = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Renderer", xpos, ypos)
        network.addConnection(plotter_processor.getOutport("outport"), mesh_renderer.getInport('inputMesh'))
        network.addConnection(plotter_processor.getOutport("labels"), mesh_renderer.getInport("imageInport"))
        ypos += 75

        background_processor = _add_processor("org.inviwo.Background", "Background", xpos, ypos)
        network.addConnection(mesh_renderer.getOutport('outputImage'), background_processor.getInport('inport'))
        ypos += 75

        text_overlay_processor = _add_processor("org.inviwo.TextOverlayGL", "Title", xpos, ypos)
        network.addConnection(background_processor.getOutport('outport'), text_overlay_processor.getInport('inport'))
        ypos += 75


        canvas_processor = _add_processor("org.inviwo.CanvasGL", "paircorrelation Canvas", xpos, ypos)
        network.addConnection(text_overlay_processor.getOutport('outport'), canvas_processor.getInport("inport"))
        ypos += 75

        # Set processor properties

        paircorrelation_processor.selection.value = "/PairCorrelationFunc"
        HDF5_to_func_processor.implicitXProperty.value = False
        HDF5_to_func_processor.xPathSelectionProperty.value = "/Distance"

        # if Elements are in h5, parsing is using _write_pcdat_multicol else _write_pcdat_onecol is used.
        if "Elements" in h5["PairCorrelationFunc"]:
            first_element = list(h5["PairCorrelationFunc/Elements"].keys())[0]
            HDF5_to_func_processor.yPathSelectionProperty.value = "/Elements/" + first_element + "/PCF for t_0"

        else:
            HDF5_to_func_processor.yPathSelectionProperty.value = "/PCF for t_0"

        plotter_processor.ySelectionProperty.value = "X"
        plotter_processor.ySelectionProperty.value = "Y"

        #Default settings of Canvas size
        canvas_processor.inputSize.dimensions.value = inviwopy.glm.ivec2(666, 367)

        # Default setting of background and Legends
        background_processor.bgColor1.value = inviwopy.glm.vec4(1)
        background_processor.backgroundStyle = "Uniform color"
        text_overlay_processor.text.value = 'Pair Correlation Function'
        text_overlay_processor.color.value = inviwopy.glm.vec2(0.42, 0.86)



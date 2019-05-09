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
##############################################################################################
#
#  Alterations to this file by Anders Rehult, Marian Brännvall, Anton Hjert,
#  Andreas Kempe and Abdullatif Ismail
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import inviwopy
import inspect, os, sys
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))
import h5py
from common import _add_h5source, _add_processor


app = inviwopy.app
network = app.network


def bandstructure(h5file, xpos = 0, ypos = 0):
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
        # A bool that tells if the band structure should be normalized around the fermi energy.
        has_fermi_energy = "/FermiEnergy" in h5

        # Start building the Inviwo network.
        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 75

        path_selection_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bandstructure", xpos, ypos)
        network.addConnection(h5source_processor.getOutport("outport"),
                              path_selection_processor.getInport("inport"))

        if has_fermi_energy:
            fermi_point_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi energy", xpos + 175, ypos)
            network.addConnection(h5source_processor.getOutport("outport"),
                                  fermi_point_processor.getInport("hdf5HandleFlatMultiInport"))

        ypos += 75

        all_children_processor = _add_processor("org.inviwo.HDF5PathSelectionAllChildren", "Select all bands", xpos, ypos)
        network.addConnection(path_selection_processor.getOutport("outport"),
                              all_children_processor.getInport("hdf5HandleInport"))
        ypos += 75

        HDF5_to_function_processor = _add_processor("org.inviwo.HDF5ToFunction", "Convert to function", xpos, ypos)
        network.addConnection(all_children_processor.getOutport("hdf5HandleVectorOutport"),
                              HDF5_to_function_processor.getInport("hdf5HandleFlatMultiInport"))
        ypos += 75

        function_to_dataframe_processor = _add_processor("org.inviwo.FunctionToDataFrame", "Convert to Data Frame", xpos, ypos)
        network.addConnection(HDF5_to_function_processor.getOutport("functionVectorOutport"),
                              function_to_dataframe_processor.getInport("functionFlatMultiInport"))
        ypos += 75
        xpos += 175

        line_plot_processor = _add_processor("org.inviwo.LinePlotProcessor", "Line plot", xpos, ypos)
        network.addConnection(function_to_dataframe_processor.getOutport("dataframeOutport"),
                              line_plot_processor.getInport("dataFrameInport"))

        if has_fermi_energy:
            network.addConnection(fermi_point_processor.getOutport("pointVectorOutport"),
                                  line_plot_processor.getInport("pointInport"))

        ypos += 75

        mesh_renderer_processor = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Mesh renderer", xpos, ypos)
        network.addConnection(line_plot_processor.getOutport("outport"),
                              mesh_renderer_processor.getInport("inputMesh"))
        network.addConnection(line_plot_processor.getOutport("labels"),
                              mesh_renderer_processor.getInport("imageInport"))
        ypos += 75

        background_processor = _add_processor("org.inviwo.Background", "Background", xpos, ypos)
        network.addConnection(mesh_renderer_processor.getOutport("outputImage"),
                              background_processor.getInport("inport"))
        ypos += 75

        energy_text_processor = _add_processor("org.inviwo.TextOverlayGL", "Energy Text", xpos, ypos)
        network.addConnection(background_processor.getOutport('outport'), energy_text_processor.getInport('inport'))
        if has_fermi_energy:
            energy_text_processor.text.value = 'Energy - Fermi energy  [eV]'
        else:
            energy_text_processor.text.value = 'Energy [eV]'
        energy_text_processor.font.fontSize.value = 20
        energy_text_processor.position.value = inviwopy.glm.vec2(0.31, 0.93)
        energy_text_processor.color.value = inviwopy.glm.vec4(0,0,0,1)

        ypos += 75

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "Canvas", xpos, ypos)
        network.addConnection(energy_text_processor.getOutport('outport'), canvas_processor.getInport('inport'))

        # Start modifying properties.
        path_selection_processor.selection.value = '/Bandstructure/Bands'
        HDF5_to_function_processor.yPathSelectionProperty.value = '/Energy'
        line_plot_processor.allYSelection.value = True
        background_processor.bgColor1.value = inviwopy.glm.vec4(1)
        background_processor.bgColor2.value = inviwopy.glm.vec4(1)
        canvas_processor.inputSize.dimensions.value = inviwopy.glm.ivec2(900, 700)
        if has_fermi_energy:
            fermi_point_processor.pathSelectionProperty.value = '/FermiEnergy'

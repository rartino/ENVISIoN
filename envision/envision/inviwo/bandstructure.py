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

        processor_list = [processor for processor, _ in inviwo.listProcessors()]

        path_selector_list = []
        hdf5_to_list = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 100

        bandstructure_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bandstructure", xpos, ypos)
        path_selector_list.append(bandstructure_processor)
        inviwo.addConnection(h5source_processor, "outport", bandstructure_processor, "inport")
        ypos += 100

        bands_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select Bands", xpos, ypos)
        path_selector_list.append(bands_processor)
        inviwo.addConnection(bandstructure_processor, "outport", bands_processor, "inport")
        ypos += 100

        all_processor = _add_processor("org.inviwo.HDF5PathSelectionAllChildren", "Select All", xpos, ypos)
        inviwo.addConnection(bands_processor, "outport", all_processor, "hdf5HandleInport")
        ypos += 100

        band_processor = _add_processor("org.inviwo.HDF5ToFunction", "To Function", xpos, ypos)
        hdf5_to_list.append(band_processor)
        inviwo.addConnection(all_processor, "hdf5HandleVectorOutport", band_processor, "hdf5HandleFlatMultiInport")
        ypos += 100

        has_fermi_energy = "/FermiEnergy" in h5
        if has_fermi_energy:
            if "Fermi Energy" in processor_list:
                fermi_energy_processor = "Fermi Energy"
            else:
                fermi_energy_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
                inviwo.addConnection(h5source_processor, "outport", fermi_energy_processor, "hdf5HandleFlatMultiInport")
                ypos += 100

        plotter_processor = _add_processor("org.inviwo.Plotter", "Band Structure Plotter", xpos, ypos)
        inviwo.addConnection(band_processor, "functionVectorOutport", plotter_processor, "functionFlatMultiInport")
        if has_fermi_energy:
            inviwo.addConnection(fermi_energy_processor, "pointVectorOutport", plotter_processor, "markYFlatMultiInport")
        ypos += 100

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "Band Structure Canvas", xpos, ypos)
        inviwo.addConnection(plotter_processor, "imageOutport", canvas_processor, "inport")

        for path_selector in path_selector_list:
            inviwo.setPropertyValue(".".join([path_selector, "selection"]), "/{}".format(path_selector.split()[1]))

        for hdf5_to in hdf5_to_list:
            inviwo.setPropertyValue(".".join([hdf5_to, "implicitXProperty"]), True)
            inviwo.setPropertyValue(".".join([hdf5_to, "yPathSelectionProperty"]), "/{}".format("Energy"))
            inviwo.setPropertyValue(".".join([hdf5_to, "yPathFreeze"]), True)

        if has_fermi_energy:
            inviwo.setPropertyValue(".".join([fermi_energy_processor, "pathSelectionProperty"]), "/{}".format("FermiEnergy"))
            inviwo.setPropertyValue(".".join([fermi_energy_processor, "pathFreeze"]), True)

        inviwo.setPropertyValue(".".join([plotter_processor, "markShiftToZeroYProperty"]), "Fermi Energy")

        inviwo.setPropertyValue(".".join([canvas_processor, "inputSize", "dimensions"]), (640, 480))

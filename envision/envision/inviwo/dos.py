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

import inviwo
import numpy as np
import h5py
from .common import _add_h5source, _add_processor

def dos(h5file, xpos=0, ypos=0):
    """Creates an Inviwo network for density of states visualization

    This function will use a suitable HDF5 source processor if one is
    already present, otherwise one will be created. Likewise, a Fermi
    energy 2D graph marker processor will be reused or created
    as is needed.

    If partial density of states data is available and a unit cell or
    molecular dynamics network is already present, this function will
    connect with it to enable visualization based on selected atoms.

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

    def get_dos_list(iter):
        return list(sorted(
            filter(lambda item: item != "Energy" and not item.startswith("Integrated"), iter),
            key=lambda item: "".join(reversed(item))
        ))

    with h5py.File(h5file,"r") as h5:

        processor_list = [processor for processor, _ in inviwo.listProcessors()]

        path_selector_list = []
        hdf5_to_function_list = []
        plotter_source_list = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 100

        dos_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select DOS", xpos, ypos)
        path_selector_list.append(dos_processor)
        inviwo.addConnection(h5source_processor, "outport", dos_processor, "inport")
        ypos += 100

        has_partial = "/DOS/Partial" in h5
        def totalpartial(name, xpos, ypos):

            totalpartial_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select {}".format(name), xpos, ypos)
            path_selector_list.append(totalpartial_processor)
            inviwo.addConnection(dos_processor, "outport", totalpartial_processor, "inport")
            totalpartial_source = totalpartial_processor, "outport"

            ypos += 100

            if name == "Partial":
                totalpartial_pick_processor = _add_processor("org.inviwo.HDF5PathSelectionAllChildren", "{} {}".format(name, "Pick All"), xpos, ypos)
                inviwo.addConnection(*totalpartial_source, totalpartial_pick_processor, "hdf5HandleInport")
                totalpartial_source = totalpartial_pick_processor, "hdf5HandleVectorOutport"

            if has_partial:
                ypos += 100

            if name == "Total":
                path = name
            else:
                path = name + "/0"
            dos_list = get_dos_list(h5["/DOS/{}".format(path)])

            y_name_prepend_parents = 2 if name == "Partial" else 1

            down_type_list = [dos for dos in dos_list if dos.endswith("(dwn)")]
            xpos_down, ypos_down = xpos, ypos
            for down_type in down_type_list:
                down_type_processor = _add_processor("org.inviwo.HDF5ToFunction", down_type, xpos_down, ypos_down)
                hdf5_to_function_list.append(down_type_processor)
                inviwo.setPropertyValue(".".join([down_type_processor, "yNamePrependParentsProperty"]), y_name_prepend_parents)
                inviwo.addConnection(*totalpartial_source, down_type_processor, "hdf5HandleFlatMultiInport")
                xpos_down += 200

            up_type_list = [dos for dos in dos_list if dos.endswith("(up)")]
            xpos_up, ypos_up = xpos_down, ypos_down
            for up_type in up_type_list:
                up_type_processor = _add_processor("org.inviwo.HDF5ToFunction", up_type, xpos_up, ypos_up)
                hdf5_to_function_list.append(up_type_processor)
                inviwo.setPropertyValue(".".join([up_type_processor, "yNamePrependParentsProperty"]), y_name_prepend_parents)
                inviwo.addConnection(*totalpartial_source, up_type_processor, "hdf5HandleFlatMultiInport")
                xpos_up += 200

            other_type_list = [dos for dos in dos_list if not dos.endswith("(dwn)") and not dos.endswith("(up)")]
            xpos_other, ypos_other = xpos_up, ypos_up
            for other_type in other_type_list:
                other_type_processor = _add_processor("org.inviwo.HDF5ToFunction", other_type, xpos_other, ypos_other)
                hdf5_to_function_list.append(other_type_processor)
                inviwo.setPropertyValue(".".join([other_type_processor, "yNamePrependParentsProperty"]), y_name_prepend_parents)
                inviwo.addConnection(*totalpartial_source, other_type_processor, "hdf5HandleFlatMultiInport")
                xpos_other += 200

            ypos += 100

            if down_type_list:
                down_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Down Add".format(name), xpos, ypos)
                inviwo.setPropertyValue(".".join([down_add_processor, "operationProperty"]), "add")
                for down_type in down_type_list:
                    inviwo.addConnection(down_type, "functionVectorOutport", down_add_processor, "functionFlatMultiInport")

            if up_type_list:
                up_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Up Add".format(name), xpos_down, ypos)
                inviwo.setPropertyValue(".".join([up_add_processor, "operationProperty"]), "add")
                for up_type in up_type_list:
                    inviwo.addConnection(up_type, "functionVectorOutport", up_add_processor, "functionFlatMultiInport")
                plotter_source_list.append(up_add_processor)

            if other_type_list:
                other_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Add".format(name), xpos_up, ypos)
                inviwo.setPropertyValue(".".join([other_add_processor, "operationProperty"]), "add")
                for other_type in other_type_list:
                    inviwo.addConnection(other_type, "functionVectorOutport", other_add_processor, "functionFlatMultiInport")
                plotter_source_list.append(other_add_processor)

            if down_type_list or up_type_list or other_type_list:
                ypos += 100

            if down_type_list:
                down_negate_processor = _add_processor("org.inviwo.FunctionOperationUnary", "{} Down Negate".format(name), xpos, ypos)
                inviwo.setPropertyValue(".".join([down_negate_processor, "operationProperty"]), "negate")
                inviwo.addConnection(down_add_processor, "functionVectorOutport", down_negate_processor, "functionFlatMultiInport")
                plotter_source_list.append(down_negate_processor)
                ypos += 100

            return xpos_other, ypos

        xpos_total, ypos_total = totalpartial("Total", xpos, ypos)
        if has_partial:
            xpos_partial, ypos_partial = totalpartial("Partial", xpos_total, ypos)
        else:
            xpos_partial, ypos_partial = 0, 0
        ypos = max(ypos_total, ypos_partial)

        has_fermi_energy = "/FermiEnergy" in h5
        if has_fermi_energy:
            if "Fermi Energy" in processor_list:
                fermi_energy_processor = "Fermi Energy"
            else:
                fermi_energy_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
                inviwo.addConnection(h5source_processor, "outport", fermi_energy_processor, "hdf5HandleFlatMultiInport")
                ypos += 100

        plotter_processor = _add_processor("org.inviwo.Plotter", "DOS Plotter", xpos, ypos)
        for plotter_source in plotter_source_list:
            inviwo.addConnection(plotter_source, "functionVectorOutport", plotter_processor, "functionFlatMultiInport")
        if has_fermi_energy:
            inviwo.addConnection(fermi_energy_processor, "pointVectorOutport", plotter_processor, "markXFlatMultiInport")

        ypos += 100

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "DOS Canvas", xpos, ypos)
        inviwo.addConnection(plotter_processor, "imageOutport", canvas_processor, "inport")

        ypos += 100

        for path_selector in path_selector_list:
            inviwo.setPropertyValue(".".join([path_selector, "selection"]), "/{}".format(path_selector.split()[1]))

        for hdf5_to_function in hdf5_to_function_list:
            inviwo.setPropertyValue(".".join([hdf5_to_function, "implicitXProperty"]), False)
            inviwo.setPropertyValue(".".join([hdf5_to_function, "xPathSelectionProperty"]), "/{}".format("Energy"))
            inviwo.setPropertyValue(".".join([hdf5_to_function, "yPathSelectionProperty"]), "/{}".format(hdf5_to_function))
            inviwo.setPropertyValue(".".join([hdf5_to_function, "xPathFreeze"]), True)
            inviwo.setPropertyValue(".".join([hdf5_to_function, "yPathFreeze"]), True)

        if has_fermi_energy:
            inviwo.setPropertyValue(".".join([fermi_energy_processor, "pathSelectionProperty"]), "/{}".format("FermiEnergy"))
            inviwo.setPropertyValue(".".join([fermi_energy_processor, "pathFreeze"]), True)

        inviwo.setPropertyValue(".".join([plotter_processor, "markShiftToZeroXProperty"]), "Fermi Energy")
        inviwo.setPropertyValue(".".join([plotter_processor, "axisLimitAutoAdjustXProperty"]), False)
        inviwo.setPropertyValue(".".join([plotter_processor, "axisLimitAutoAdjustYProperty"]), False)

        inviwo.setPropertyValue(".".join([canvas_processor, "inputSize", "dimensions"]), (640, 480))

        if has_partial and "Unit Cell Mesh" in processor_list:

            def get_child_list(parent):
                return [
                    child
                    for [[processor, _], [child, _]] in inviwo.getConnections()
                    if processor == parent
                ]

            def get_parent_list(child):
                return [
                    parent
                    for [[parent, _], [processor, _]] in inviwo.getConnections()
                    if processor == child
                ]

            partial_pick_all_position = inviwo.getProcessorPosition("Partial Pick All")
            partial_pick_all_child_list = get_child_list("Partial Pick All")
            partial_pick_all_parent_list = get_parent_list("Partial Pick All")

            inviwo.removeProcessor("Partial Pick All")
            partial_pick_processor = _add_processor("org.inviwo.HDF5PathSelectionIntVector", "Partial Pick", *partial_pick_all_position)

            ypos += 100

            for partial_pick_all_child in partial_pick_all_child_list:
                inviwo.addConnection(partial_pick_processor, "hdf5HandleVectorOutport", partial_pick_all_child, "hdf5HandleFlatMultiInport")
            for partial_pick_all_parent in partial_pick_all_parent_list:
                inviwo.addConnection(partial_pick_all_parent, "outport", partial_pick_processor, "hdf5HandleInport")
            inviwo.addLink(".".join(["Unit Cell Mesh", "inds"]), ".".join(["Partial Pick", "intVectorProperty"]))
            inviwo.setPropertyValue(".".join(["Unit Cell Mesh", "enablePicking"]), True)

            dos_unitcell_layout_processor = _add_processor("org.inviwo.ImageLayoutGL", "DOS UnitCell Layout", xpos, ypos)
            inviwo.addConnection("Unit Cell Renderer", "image", dos_unitcell_layout_processor, "multiinport")
            inviwo.addConnection("DOS Plotter", "imageOutport", dos_unitcell_layout_processor, "multiinport")

            ypos += 100

            dos_unitcell_canvas_processor = _add_processor("org.inviwo.CanvasGL", "DOS UnitCell Canvas", xpos, ypos)
            inviwo.setPropertyValue(".".join([dos_unitcell_canvas_processor, "inputSize", "dimensions"]), (2 * 640, 480))
            inviwo.addConnection(dos_unitcell_layout_processor, "outport", dos_unitcell_canvas_processor, "inport")

            ypos += 100

            inviwo.setPropertyValue(".".join([dos_unitcell_layout_processor, "layout"]), 2)

            inviwo.setProcessorWidgetVisible("DOS Canvas", False)
            inviwo.setProcessorWidgetVisible("Unit Cell Canvas", False)
            inviwo.setProcessorWidgetVisible(dos_unitcell_canvas_processor, True)


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

        processor_list = network.processors

        path_selector_list = []
        hdf5_to_function_list = []
        plotter_source_list = []

        h5source_processor = _add_h5source(h5file, xpos, ypos)
        ypos += 100

        dos_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select DOS", xpos, ypos)
        path_selector_list.append(dos_processor)
        h5source_outport = h5source_processor.getOutport('outport')
        dos_inport = dos_processor.getInport('inport')
        network.addConnection(h5source_outport, dos_inport)
        ypos += 100

        has_partial = "/DOS/Partial" in h5
        def totalpartial(name, xpos, ypos):

            totalpartial_processor = _add_processor("org.inviwo.hdf5.PathSelection", "Select {}".format(name), xpos, ypos)
            path_selector_list.append(totalpartial_processor)
            dos_outport = dos_processor.getOutport('outport')
            totalpartial_inport = totalpartial_processor.getInport('inport')
            network.addConnection(dos_outport, totalpartial_inport)

            ypos += 100

            if name == "Partial":
                totalpartial_pick_processor = _add_processor("org.inviwo.HDF5PathSelectionAllChildren", "{} {}".format(name, "Pick All"), xpos, ypos)
                totalpartial_outport = totalpartial_processor.getOutport('outport')
                totalpartial_pick_inport = totalpartial_pick_processor.getInport('hdf5HandleInport')

            if has_partial:
                ypos += 100

            if name == "Total":
                path = name
            else:
                path = name + "/0"
            dos_list = get_dos_list(h5["/DOS/{}".format(path)])

            y_name_prepend_parents = 2 if name == "Partial" else 1

            down_type_list = [dos for dos in dos_list if dos.endswith("(dwn)")]
            for dos in down_type_list:
                print(dos)
            xpos_down, ypos_down = xpos, ypos
            for down_type in down_type_list:
                down_type_processor = _add_processor("org.inviwo.HDF5ToFunction", down_type, xpos_down, ypos_down)
                hdf5_to_function_list.append(down_type_processor)

                down_type_y_name_property = down_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                down_type_y_name_property.value = y_name_prepend_parents

                """totalpartial_source_hdf5outport = totalpartial_pick_processor.getOutport('hdf5HandleVectorOutport')
                down_type_processor_hdf5inport = down_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_source_hdf5outport, down_type_processor_hdf5inport)"""
                
                totalpartial_outport = totalpartial_processor.getOutport('outport')
                down_type_hdf5inport = down_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_outport, down_type_hdf5inport)
            
                xpos_down += 200
            
            up_type_list = [dos for dos in dos_list if dos.endswith("(up)")]
            xpos_up, ypos_up = xpos_down, ypos_down
            for up_type in up_type_list:
                up_type_processor = _add_processor("org.inviwo.HDF5ToFunction", up_type, xpos_up, ypos_up)
                hdf5_to_function_list.append(up_type_processor)
                up_type_y_name_property = up_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                up_type_y_name_property.value = y_name_prepend_parents

                totalpartial_outport = totalpartial_processor.getOutport('outport')
                up_type_hdf5inport = up_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_outport, up_type_hdf5inport)

                xpos_up += 200

            other_type_list = [dos for dos in dos_list if not dos.endswith("(dwn)") and not dos.endswith("(up)")]
            xpos_other, ypos_other = xpos_up, ypos_up
            for other_type in other_type_list:
                other_type_processor = _add_processor("org.inviwo.HDF5ToFunction", other_type, xpos_other, ypos_other)
                hdf5_to_function_list.append(other_type_processor)

                other_type_y_name_property = other_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                other_type_y_name_property.value = y_name_prepend_parents

                totalpartial_outport = totalpartial_processor.getOutport('outport')
                other_type_hdf5inport = other_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_outport, other_type_hdf5inport)

                xpos_other += 200

            ypos += 100

            if down_type_list:
                down_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Down Add".format(name), xpos, ypos)
                down_add_operation_property = down_add_processor.getPropertyByIdentifier('operationProperty')
                down_add_operation_property.value = 'add'

                down_add_inport = down_add_processor.getInport('functionFlatMultiInport')
                for down_type in down_type_list:
                    down_type_processor = network.getProcessorByIdentifier(down_type)
                    down_type_outport = down_type_processor.getOutport('functionVectorOutport')
                    network.addConnection(down_type_outport, down_add_inport)

            if up_type_list:
                up_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Up Add".format(name), xpos_down, ypos)
                up_add_operation_property = up_add_processor.getPropertyByIdentifier('operationProperty')
                up_add_operation_property.value = 'add'


                up_add_inport = up_add_processor.getInport('functionFlatMultiInport')
                for up_type in up_type_list:
                    up_type_processor = network.getProcessorByIdentifier(up_type)
                    up_outport = up_type_processor.getOutport('functionVectorOutport')
                    network.addConnection(up_outport, up_add_inport)
                plotter_source_list.append(up_add_processor)

            if other_type_list:
                other_add_processor = _add_processor("org.inviwo.FunctionOperationNary", "{} Add".format(name), xpos_up, ypos)
                other_add_operation_property = other_add_processor.getPropertyByIdentifier('operationProperty')
                other_add_operation_property.value = 'add'

                other_add_inport = other_add_processor.getInport('functionFlatMultiInport')
                for other_type in other_type_list:
                    other_type_processor = network.getProcessorByIdentifier(other_type)
                    other_outport = other_type_processor.getOutport('functionVectorOutport')
                    network.addConnection(other_outport, other_add_inport)
                plotter_source_list.append(other_add_processor)

            if down_type_list or up_type_list or other_type_list:
                ypos += 100

            if down_type_list:
                down_negate_processor = _add_processor("org.inviwo.FunctionOperationUnary", "{} Down Negate".format(name), xpos, ypos)
                down_negate_operation_property = down_negate_processor.getPropertyByIdentifier('operationProperty')
                down_negate_operation_property.value = 'negate'

                #down_negate_inport = down_negate_processor.getInport('functionFlatMultiInport')
                down_negate_inport = down_negate_processor.getInport('dataframeInport')
                #down_add_outport = down_add_processor.getOutport('functionVectorOutport')
                down_add_outport = down_add_processor.getOutport('dataframeOutport')
                # Only works with cu 1 10
                network.addConnection(down_add_outport, down_negate_inport)
                plotter_source_list.append(down_negate_processor)
                ypos += 100

            return xpos_other, ypos

        xpos_total, ypos_total = totalpartial("Total", xpos, ypos)
        if has_partial:
            xpos_partial, ypos_partial = totalpartial("Partial", xpos_total, ypos)
        else:
            xpos_partial, ypos_partial = 0, 0
        ypos = max(ypos_total, ypos_partial)

        """has_fermi_energy = "/FermiEnergy" in h5
        if has_fermi_energy:
            if "Fermi Energy" in processor_list:
                fermi_energy_processor = "Fermi Energy"
            else:
                fermi_energy_processor = _add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
                h5source_outport = h5source_processor.getOutport('outport')
                fermi_energy_inport = fermi_energy_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(h5source_outport, fermi_energy_inport)
                ypos += 100"""
        
        
        for plotter_source in plotter_source_list: 
            plotter_processor = _add_processor("org.inviwo.lineplotprocessor", "DOS Plotter", xpos, ypos) 
            plotter_source_outport = plotter_source.getOutport('dataframeOutport')
            plotter_processor_labels_outport = plotter_processor.getOutport('labels')
            plotter_processor_mesh_outport = plotter_processor.getOutport('outport')
            plotter_processor_inport = plotter_processor.getInport('dataFrameInport')
            help(plotter_processor.getPropertyByIdentifier('font'))
            #plotter_processor.getPropertyByIdentifier('font').getPropertyByIdentifier('anchor').value = inviwopy.glm.vec2(-1, -0.96)
            network.addConnection(plotter_source_outport, plotter_processor_inport)
        
            ypos += 100
            
            mesh_renderer = _add_processor("org.inviwo.Mesh2DRenderProcessorGL", "Renderer", xpos, ypos) 
            mesh_renderer_inport = mesh_renderer.getInport('inputMesh')
            mesh_renderer_inport_image = mesh_renderer.getInport('imageInport')
            mesh_renderer_outport = mesh_renderer.getOutport('outputImage')
            network.addConnection(plotter_processor_mesh_outport, mesh_renderer_inport)
            network.addConnection(plotter_processor_labels_outport, mesh_renderer_inport_image)
            
            ypos += 100
            
            background_processor = _add_processor("org.inviwo.Background", "Background", xpos, ypos)
            background_processor_inport = background_processor.getInport('inport')
            background_processor_outport = background_processor.getOutport('outport')
            background_processor.getPropertyByIdentifier('bgColor1').value = inviwopy.glm.vec4(1, 1, 1, 1)
            background_processor.getPropertyByIdentifier('bgColor2').value = inviwopy.glm.vec4(1, 1, 1, 1)
            network.addConnection(mesh_renderer_outport, background_processor_inport)
            
            ypos += 100
      
            canvas_processor = _add_processor("org.inviwo.CanvasGL", "Canvas", xpos, ypos)
            canvas_inport = canvas_processor.getInport('inport')
            network.addConnection(background_processor_outport, canvas_inport)

            
            ypos += 100  
            xpos += 100
            
        """
        plotter_processor = _add_processor("org.inviwo.Plotter", "DOS Plotter", xpos, ypos)
        for plotter_source in plotter_source_list:
            plotter_source_outport = plotter_source.getOutport('functionVectorOutport')
            plotter_processor_inport = plotter_processor.getInport('functionFlatMultiInport')
            network.addConnection(plotter_source_outport, plotter_processor_inport)
        if has_fermi_energy:
            fermi_outport = fermi_energy_processor.getOutport('pointVectorOutport')
            plotter_inport = plotter_processor.getInport('markXFlatMultiInport')
            network.addConnection(fermi_outport, plotter_inport)
 
        ypos += 100

        canvas_processor = _add_processor("org.inviwo.CanvasGL", "DOS Canvas", xpos, ypos)
        plotter_outport = plotter_processor.getOutport('imageOutport')
        canvas_inport = canvas_processor.getInport('inport')
        network.addConnection(plotter_outport, canvas_inport)

        ypos += 100

        for path_selector in path_selector_list:
            path_selector.getPropertyByIdentifier('selection').value = '/{}'.format(path_selector.split()[1])

        for hdf5_to_function in hdf5_to_function_list:
            hdf5_to_function.getPropertyByIdentifier('implicitXProperty').value = False
            hdf5_to_function.getPropertyByIdentifier('xPathSelectionProperty').value = '/{}'.format("Energy")
            hdf5_to_function.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(hdf5_to_function)
            hdf5_to_function.getPropertyByIdentifier('xPathFreeze').value = True
            hdf5_to_function.getPropertyByIdentifier('yPathFreeze').value = True

        if has_fermi_energy:
            fermi_energy_processor.getPropertyByIdentifier('pathSelectionProperty').value = '/{}'.format("FermiEnergy")
            fermi_energy_processor.getPropertyByIdentifier('pathFreeze').value = True

        plotter_processor.getPropertyByIdentifier('markShiftToZeroXProperty').value = 'Fermi Energy'
        plotter_processor.getPropertyByIdentifier('axisLimitAutoAdjustXProperty').value = False
        plotter_processor.getPropertyByIdentifier('axisLimitAutoAdjustYProperty').value = False

        canvas_processor.getPropertyByIdentifier('inputSize.dimensions').value = (640, 480)

        """
        ## TODO: Find out why the Partial Pick All processor isn't connected to anything at the start of this block.
        # Replaces Partial Pick All processor with Partial Pick processor.
        if has_partial and "Unit Cell Mesh" in [x.identifier for x in processor_list]:
            
            def get_child_list(parent):
                child_list = []
                for connection in network.connections:
                    if connection.outport.processor == parent:
                         child_list.append(connection.inport.processor)
                return child_list
                
            def get_parent_list(child):
                parent_list = []
                for connection in network.connections:
                    if connection.inport.processor == child:
                         parent_list.append(connection.outport.processor)
                return parent_list
            """                
            def get_child_list(parent):
                return [
                    child
                    for [[processor, _], [child, _]] in network.connections
                    if processor == parent
                ]

            def get_parent_list(child):
                return [
                    parent
                    for [[parent, _], [processor, _]] in inviwopy.getConnections()
                    if processor == child
                ]
            """

            partial_pick_all_position = network.getProcessorByIdentifier("Partial Pick All").position
            partial_pick_all_child_list = get_child_list(network.getProcessorByIdentifier("Partial Pick All"))
            partial_pick_all_parent_list = get_parent_list(network.getProcessorByIdentifier("Partial Pick All"))

            network.removeProcessor(network.getProcessorByIdentifier("Partial Pick All"))
            partial_pick_processor = _add_processor("org.inviwo.HDF5PathSelectionIntVector", "Partial Pick", partial_pick_all_position[0], partial_pick_all_position[1])

            ypos += 100
            for partial_pick_all_child in partial_pick_all_child_list:
                network.addConnection(partial_pick_processor.getOutport("hdf5HandleVectorOutport"), partial_pick_all_child.getInport("hdf5HandleFlatMultiInport"))
            for partial_pick_all_parent in partial_pick_all_parent_list:
                network.addConnection(partial_pick_all_parent.getOutport("outport"), partial_pick_processor.getInport("hdf5HandleInport"))
            network.addLink(network.getProcessorByIdentifier("Unit Cell Mesh").getPropertyByIdentifier("inds"), network.getProcessorByIdentifier("Partial Pick").getPropertyByIdentifier("intVectorProperty"))
            #network.addLink(".".join(["Unit Cell Mesh", "inds"]), ".".join(["Partial Pick", "intVectorProperty"]))
            network.getProcessorByIdentifier("Unit Cell Mesh").getPropertyByIdentifier("enablePicking").value = True
            #inviwopy.setPropertyValue(".".join(["Unit Cell Mesh", "enablePicking"]), True)

            dos_unitcell_layout_processor = _add_processor("org.inviwo.ImageLayoutGL", "DOS UnitCell Layout", xpos, ypos)
            network.addConnection(network.getProcessorByIdentifier("Unit Cell Renderer").getOutport("image"), dos_unitcell_layout_processor.getInport("multiinport"))
            network.addConnection(network.getProcessorByIdentifier("DOS Plotter").getOutport("outport"), dos_unitcell_layout_processor.getInport("multiinport"))
            #inviwopy.addConnection("DOS Plotter", "imageOutport", dos_unitcell_layout_processor, "multiinport")

            ypos += 100

            dos_unitcell_canvas_processor = _add_processor("org.inviwo.CanvasGL", "DOS UnitCell Canvas", xpos, ypos)
            dos_unitcell_canvas_processor.getPropertyByIdentifier("inputSize").getPropertyByIdentifier("dimensions").value = inviwopy.glm.ivec2(2 * 640, 480)
            #inviwopy.setPropertyValue(".".join([dos_unitcell_canvas_processor, "inputSize", "dimensions"]), (2 * 640, 480))
            network.addConnection(dos_unitcell_layout_processor.getOutport("outport"), dos_unitcell_canvas_processor.getInport("inport"))
            #inviwopy.addConnection(dos_unitcell_layout_processor, "outport", dos_unitcell_canvas_processor, "inport")
            ypos += 100
            
            dos_unitcell_canvas_processor.getPropertyByIdentifier("layout").value = 2
            #inviwopy.setPropertyValue(".".join([dos_unitcell_layout_processor, "layout"]), 2)
            
            network.getProcessorByIdentifier("DOS Canvas").widget.visibility = False
            network.getProcessorByIdentifier("Unit Cell Canvas").widget.visibility = False
            dos_unitcell_canvas_processor.widget.visibility = True

            #inviwopy.setProcessorWidgetVisible("DOS Canvas", False)
            #inviwopy.setProcessorWidgetVisible("Unit Cell Canvas", False)
            #inviwopy.setProcessorWidgetVisible(dos_unitcell_canvas_processor, True)


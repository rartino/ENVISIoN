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

def dos(h5file, atom = 0, xpos=0, ypos=0):
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
    atom : int
         (Default value = 0)
         Index of atom for which to visualise partial DOS.
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

        # Inviwo will not set path selection properties until the network is fully formed. These lists
        # store the relevant processors for later configuration (see end of file).
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
            totalpartial_outport = totalpartial_processor.getOutport('outport')
            network.addConnection(dos_outport, totalpartial_inport)

            ypos += 100

            if name == "Partial":
                path = name
                totalpartial_pick_processor = _add_processor("org.inviwo.HDF5PathSelectionInt", "{} {}".format(name, "Pick"), xpos, ypos)
                # TODO: Setting this value hangs Inviwo.
                #totalpartial_pick_int = totalpartial_pick_processor.getPropertyByIdentifier('intProperty')
                #totalpartial_pick_int.value = atom
                totalpartial_pick_inport = totalpartial_pick_processor.getInport('hdf5HandleInport')
                network.addConnection(totalpartial_outport, totalpartial_pick_inport)
                totalpartial_pick_outport = totalpartial_pick_processor.getOutport('hdf5HandleVectorOutport')
                totalpartial_outport = totalpartial_pick_outport

            if has_partial:
                ypos += 100

            if name == "Total":
                path = name
            else:
                path = name + '/{}'.format(atom)
            dos_list = get_dos_list(h5["/DOS/{}".format(path)])

            y_name_prepend_parents = 2 if name == "Partial" else 1

            down_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if dos.endswith("(dwn)")]
            xpos_down, ypos_down = xpos, ypos
            for down_type in down_type_list:
                down_type_processor = _add_processor("org.inviwo.HDF5ToFunction", down_type, xpos_down, ypos_down)
                hdf5_to_function_list.append(down_type_processor)

                down_type_y_name_property = down_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                down_type_y_name_property.value = y_name_prepend_parents

                down_type_hdf5inport = down_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_outport, down_type_hdf5inport)
            
                xpos_down += 200
            
            up_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if dos.endswith("(up)")]
            xpos_up, ypos_up = xpos_down, ypos_down
            for up_type in up_type_list:
                up_type_processor = _add_processor("org.inviwo.HDF5ToFunction", up_type, xpos_up, ypos_up)
                hdf5_to_function_list.append(up_type_processor)
                up_type_y_name_property = up_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                up_type_y_name_property.value = y_name_prepend_parents
                up_type_hdf5inport = up_type_processor.getInport('hdf5HandleFlatMultiInport')
                network.addConnection(totalpartial_outport, up_type_hdf5inport)

                xpos_up += 200

            other_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if not dos.endswith("(dwn)") and not dos.endswith("(up)")]
            xpos_other, ypos_other = xpos_up, ypos_up
            for other_type in other_type_list:
                other_type_processor = _add_processor("org.inviwo.HDF5ToFunction", other_type, xpos_other, ypos_other)
                hdf5_to_function_list.append(other_type_processor)

                other_type_y_name_property = other_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                other_type_y_name_property.value = y_name_prepend_parents
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

                down_negate_inport = down_negate_processor.getInport('dataframeInport')
                down_add_outport = down_add_processor.getOutport('dataframeOutport')
                network.addConnection(down_add_outport, down_negate_inport)
                plotter_source_list.append(down_negate_processor)
                ypos += 100
            return xpos_other, ypos

        xpos_total, ypos_total = totalpartial("Total", xpos, ypos)
        if has_partial:
            ypos_partial = 0
            xpos_partial, ypos_partial_new = totalpartial("Partial", xpos_total, ypos)
            ypos_partial = max(ypos_partial, ypos_partial_new)
            
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

            
            energy_text_processor = _add_processor("org.inviwo.TextOverlayGL", "Energy Text", xpos, ypos)
            energy_text_processor.getPropertyByIdentifier('text').value = 'Energy [eV]'
            energy_text_processor.getPropertyByIdentifier('position').value = inviwopy.glm.vec2(0.82, 0.03)
            energy_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0,0,0,1)
            energy_text_processor_inport = energy_text_processor.getInport('inport')
            energy_text_processor_outport = energy_text_processor.getOutport('outport')
            network.addConnection(background_processor_outport, energy_text_processor_inport)
            
            ypos += 100
            
            dos_text_processor = _add_processor("org.inviwo.TextOverlayGL", "DOS Text", xpos, ypos)
            dos_text_processor.getPropertyByIdentifier('text').value = 'DOS [1/(eV * unit cell)]'
            dos_text_processor.getPropertyByIdentifier('position').value = inviwopy.glm.vec2(0.31, 0.93)
            dos_text_processor.getPropertyByIdentifier('color').value = inviwopy.glm.vec4(0,0,0,1)
            dos_text_processor_inport = dos_text_processor.getInport('inport')
            dos_text_processor_outport = dos_text_processor.getOutport('outport')
            network.addConnection(energy_text_processor_outport, dos_text_processor_inport)
            
            ypos += 100
      
            canvas_processor = _add_processor("org.inviwo.CanvasGL", "DOS Canvas", xpos, ypos)
            canvas_inport = canvas_processor.getInport('inport')
            canvas_processor.getPropertyByIdentifier('inputSize').getPropertyByIdentifier('dimensions').value= inviwopy.glm.ivec2(640, 480)
            network.addConnection(dos_text_processor_outport, canvas_inport)

            ypos += 100  
            xpos += 100

        # Selects correct paths.
        for path_selector in path_selector_list:
            path_selector.getPropertyByIdentifier('selection').value = '/{}'.format(path_selector.identifier.split()[1])
        for hdf5_to_function in hdf5_to_function_list:
            hdf5_to_function.getPropertyByIdentifier('implicitXProperty').value = False
            hdf5_to_function.getPropertyByIdentifier('xPathSelectionProperty').value = '/{}'.format("Energy")
            hdf5_to_function.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(hdf5_to_function.identifier)
            hdf5_to_function.getPropertyByIdentifier('xPathFreeze').value = True
            hdf5_to_function.getPropertyByIdentifier('yPathFreeze').value = True


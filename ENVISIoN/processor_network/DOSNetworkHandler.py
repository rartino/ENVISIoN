#
#  ENVISIoN
#
#  Copyright (c) 2017-2019 Robert Cranston, Anders Rehult, Viktor Bernholtz, Marian Brännvall, Jesper Ericsson
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


import sys
import os
import inspect
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy
import numpy as np
import h5py


from .LinePlotNetworkHandler import LinePlotNetworkHandler
from .UnitcellNetworkHandler import UnitcellNetworkHandler
from envision.utils.exceptions import *


class DOSNetworkHandler(LinePlotNetworkHandler, UnitcellNetworkHandler):
    """ Handler class for charge visualizationself.network.
        Sets up and manages the charge visualization
    """

    def __init__(self, hdf5_path, inviwoApp):
        LinePlotNetworkHandler.__init__(self, inviwoApp)

        # Unitcell is not critical to visualization, if it fails, continnue anyway
        self.unitcellAvailable = True
        try: 
            UnitcellNetworkHandler.__init__(self, hdf5_path, inviwoApp)
        except BadHDF5Error as error:
            self.unitcellAvailable = False
        self.setup_PCF_network(hdf5_path)


    def get_ui_data(self):
    # Return data required to fill user interface
        return [
            self.get_x_range(),
            self.get_y_range(),
            self.get_label_count(),
            self.get_available_datasets()
            ]
# ------------------------------------------
# ------- Network building functions -------

    # def get_dos_list(self, iter):
    #     return list(sorted(
    #         filter(lambda item: item != "Energy", iter),
    #         key=lambda item: "".join(reversed(item))
    #     ))

    def setup_PCF_network(self, hdf5_path, atom=0, xpos=0, ypos=0):
        def get_dos_list(iter):
            return list(sorted(
                filter(lambda item: item != "Energy", iter),
                key=lambda item: "".join(reversed(item))
            ))

        with h5py.File(hdf5_path,"r") as h5:
            # Inviwo will not set path selection properties until the network is fully formed. These lists
            # store the relevant processors for later configuration (see end of file).
            path_selector_list = []
            hdf5_to_function_list = []
            unary_processor_list = []
            nary_processor_list = []
            other_add_list = []

            h5source_processor = self.add_h5source(hdf5_path, xpos, ypos)
            ypos += 75

            dos_processor = self.add_processor("org.inviwo.hdf5.PathSelection", "Select DOS", xpos, ypos)
            path_selector_list.append(dos_processor)
            h5source_outport = h5source_processor.getOutport('outport')
            dos_inport = dos_processor.getInport('inport')
            self.network.addConnection(h5source_outport, dos_inport)
            ypos += 75

            has_partial = "/DOS/Partial" in h5
            def totalpartial(name, xpos, ypos):
                totalpartial_processor = self.add_processor("org.inviwo.hdf5.PathSelection", "Select {}".format(name), xpos, ypos)
                path_selector_list.append(totalpartial_processor)
                dos_outport = dos_processor.getOutport('outport')
                totalpartial_inport = totalpartial_processor.getInport('inport')
                totalpartial_outport = totalpartial_processor.getOutport('outport')
                self.network.addConnection(dos_outport, totalpartial_inport)

                ypos += 75

                if name == "Partial":
                    totalpartial_pick_processor = self.add_processor("org.inviwo.HDF5PathSelectionInt", "{} {}".format(name, "Pick"), xpos, ypos)

                    totalpartial_pick_int = totalpartial_pick_processor.getPropertyByIdentifier('intProperty')
                    totalpartial_pick_int.value = atom
                    totalpartial_pick_int.minValue = 0
                    totalpartial_pick_int.maxValue = len(h5['/DOS/Partial']) - 1

                    totalpartial_pick_inport = totalpartial_pick_processor.getInport('hdf5HandleInport')
                    self.network.addConnection(totalpartial_outport, totalpartial_pick_inport)
                    totalpartial_pick_outport = totalpartial_pick_processor.getOutport('hdf5HandleVectorOutport')
                    totalpartial_outport = totalpartial_pick_outport

                if has_partial:
                    ypos += 75

                if name == "Total":
                    path = name
                else:
                    path = name + '/{}'.format(atom)
                dos_list = get_dos_list(h5["/DOS/{}".format(path)])

                y_name_prepend_parents = 2 if name == "Partial" else 1

                down_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if dos.endswith("(dwn)")]
                xpos_down = xpos
                for down_type in down_type_list:
                    ypos_down = ypos
                    down_type_processor = self.add_processor("org.inviwo.HDF5ToFunction", down_type, xpos_down, ypos_down)
                    self.network.addConnection(totalpartial_outport, down_type_processor.getInport('hdf5HandleFlatMultiInport'))
                    down_type_processor.yNamePrependParentsProperty.value = y_name_prepend_parents

                    ypos_down += 75

                    down_add_processor = self.add_processor("org.inviwo.FunctionOperationNary", "{} Down Add".format(name), xpos_down, ypos_down)
                    self.network.addConnection(down_type_processor.getOutport("functionVectorOutport"), down_add_processor.getInport("functionFlatMultiInport"))
                    down_add_processor.operationProperty.value = 'add'

                    ypos_down += 75

                    down_negate_processor = self.add_processor("org.inviwo.FunctionOperationUnary", "{} Down Negate".format(name), xpos_down, ypos_down)
                    self.network.addConnection(down_add_processor.getOutport("dataframeOutport"), down_negate_processor.getInport("dataframeInport"))
                    down_negate_processor.operationProperty.value = 'negate'

                    hdf5_to_function_list.append(down_type_processor)
                    unary_processor_list.append(down_negate_processor)
                    xpos_down += 175

                up_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if dos.endswith("(up)")]
                xpos_up = xpos_down
                for up_type in up_type_list:
                    ypos_up = ypos
                    up_type_processor = self.add_processor("org.inviwo.HDF5ToFunction", up_type, xpos_up, ypos_up)
                    self.network.addConnection(totalpartial_outport, up_type_processor.getInport('hdf5HandleFlatMultiInport'))
                    up_type_processor.yNamePrependParentsProperty.value = y_name_prepend_parents

                    ypos_up += 75

                    up_add_processor = self.add_processor("org.inviwo.FunctionOperationNary", "{} Down Add".format(name), xpos_up, ypos_up)
                    self.network.addConnection(up_type_processor.getOutport("functionVectorOutport"), up_add_processor.getInport("functionFlatMultiInport"))
                    up_add_processor.operationProperty.value = 'add'

                    hdf5_to_function_list.append(up_type_processor)
                    nary_processor_list.append(up_add_processor)
                    xpos_up += 175

                other_type_list = ['{} {}'.format(dos, atom) for dos in dos_list if not dos.endswith("(dwn)") and not dos.endswith("(up)")]
                xpos_other, ypos_other = xpos_up, ypos
                for other_type in other_type_list:
                    other_type_processor = self.add_processor("org.inviwo.HDF5ToFunction", other_type, xpos_other, ypos_other)
                    hdf5_to_function_list.append(other_type_processor)

                    other_type_hdf5inport = other_type_processor.getInport('hdf5HandleFlatMultiInport')
                    self.network.addConnection(totalpartial_outport, other_type_hdf5inport)

                    other_type_y_name_property = other_type_processor.getPropertyByIdentifier('yNamePrependParentsProperty')
                    other_type_y_name_property.value = y_name_prepend_parents

                    xpos_other += 175

                ypos_other += 75

                if other_type_list:
                    other_add_processor = self.add_processor("org.inviwo.FunctionOperationNary", "{} Add".format(name), xpos_up, ypos_other)
                    other_add_operation_property = other_add_processor.getPropertyByIdentifier('operationProperty')
                    other_add_operation_property.value = 'add'

                    other_add_inport = other_add_processor.getInport('functionFlatMultiInport')
                    for other_type in other_type_list:
                        other_type_processor = self.get_processor(other_type)
                        other_outport = other_type_processor.getOutport('functionVectorOutport')
                        self.network.addConnection(other_outport, other_add_inport)
                    other_add_list.append(other_add_processor)

                return xpos_other, ypos + 225

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
                    fermi_energy_processor = self.add_processor("org.inviwo.HDF5ToPoint", "Fermi Energy", xpos, ypos)
                    h5source_outport = h5source_processor.getOutport('outport')
                    fermi_energy_inport = fermi_energy_processor.getInport('hdf5HandleFlatMultiInport')
                    self.network.addConnection(h5source_outport, fermi_energy_inport)
                    ypos += 100"""

            collector = self.add_processor("org.inviwo.DataFrameCollector", "Collect", xpos, ypos)
            for unary_processor in unary_processor_list:
                self.network.addConnection(unary_processor.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))
            for nary_processor in nary_processor_list:
                self.network.addConnection(nary_processor.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))
            for other_add_processor in other_add_list:
                self.network.addConnection(other_add_processor.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))

            ypos += 75


            self.remove_processor("Function to dataframe")
            plotter_processor = self.get_processor("Line plot")
            self.network.addConnection(collector.getOutport("dataframeOutport"), plotter_processor.getInport('dataFrameInport'))

            self.set_title('DOS [1/(eV * unit cell)]')

            # canvas_processor = self.add_processor("org.inviwo.CanvasGL", "DOS Canvas", xpos, ypos)
            # self.network.addConnection(dos_text_processor.getOutport('outport'), canvas_processor.getInport('inport'))
            # canvas_processor.inputSize.dimensions.value= inviwopy.glm.ivec2(640, 480)
            
            # self.network.removeConnection(collector.getOutport("dataframeOutport"), plotter_processor.getInport('dataFrameInport'))
            self.set_y_selection_type(1)


            # Check for a Unit Cell Mesh processor and connect it for
            # picking of specific atoms if it exists, i.e. connect the two
            # properties describing what atom has been selected/should be
            # shown.
            # self.app.update()
            self.toggle_graph_canvas(False)
            # self.app.update()
            unit_cell_processor = self.network.getProcessorByIdentifier('Unit Cell Mesh')
            partial_pick_processor = self.network.getProcessorByIdentifier('Partial Pick')
            if has_partial and unit_cell_processor is not None and partial_pick_processor is not None:
                unit_cell_property = unit_cell_processor.getPropertyByIdentifier('pickedIndex')
                partial_pick_processor = partial_pick_processor.getPropertyByIdentifier('intProperty')
                self.network.addLink(unit_cell_property, partial_pick_processor)

                # Enable the possibility of picking atoms.
                pick_enable = unit_cell_processor.getPropertyByIdentifier('enablePicking')
                pick_enable.value = True

            # Selects correct paths.
            for path_selector in path_selector_list:
                path_selector.getPropertyByIdentifier('selection').value = '/{}'.format(path_selector.identifier.split()[1])
            for hdf5_to_function in hdf5_to_function_list:
                hdf5_to_function.getPropertyByIdentifier('implicitXProperty').value = False
                hdf5_to_function.getPropertyByIdentifier('xPathSelectionProperty').value = '/Energy'
                hdf5_to_function.getPropertyByIdentifier('yPathSelectionProperty').value = '/{}'.format(hdf5_to_function.identifier.split(' ')[0])
                hdf5_to_function.getPropertyByIdentifier('xPathFreeze').value = True
                hdf5_to_function.getPropertyByIdentifier('yPathFreeze').value = True
            
            # self.network.addConnection(collector.getOutport("dataframeOutport"), plotter_processor.getInport('dataFrameInport'))
            self.set_y_selection_type(2)
            self.toggle_graph_canvas(True)

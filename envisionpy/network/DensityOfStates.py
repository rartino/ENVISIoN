import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
import time
from envisionpy.utils.exceptions import *
from .baseNetworks.LinePlotSubnetwork import LinePlotSubnetwork

class DensityOfStates(LinePlotSubnetwork):
    '''
    Manages a subnetwork for density of states (DoS) visualisation. 
    
    Uses a modified LinePlotSubnetwork. Dataframes are not read directly from 
    hdf5 file but are processed before sent to the line plot processor.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        LinePlotSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, False)
        self.modify_network(hdf5_path, hdf5_outport, xpos, ypos)

        self.totalEnabled = True
        self.partialEnabled = True
        self.set_title('DOS [1/(eV * unit cell)]')

    @staticmethod
    def valid_hdf5(hdf5_file):
        return '/DOS' in hdf5_file and '/DOS/Partial' in hdf5_file and '/DOS/Total' in hdf5_file

    def get_ui_data(self):
        return []

    def toggle_total(self, enable):
        self.totalEnabled = enable
        totalCollector = self.get_processor("TotalCollector")
        collector = self.get_processor("Collector")
        if enable:
            self.network.addConnection(totalCollector.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))
        else:
            self.network.removeConnection(totalCollector.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))
    
    def toggle_partial(self, enable):
        self.partialEnabled = enable
        partialCollector = self.get_processor("PartialCollector")
        collector = self.get_processor("Collector")
        if enable:
            self.network.addConnection(partialCollector.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))
        else:
            self.network.removeConnection(partialCollector.getOutport("dataframeOutport"), collector.getInport("dataframeMultiInport"))

    def get_n_partials(self):
        return self.get_processor("Select Partial Band").intProperty.maxValue

    def set_partial_selection(self, n):
        self.get_processor("Select Partial Band").intProperty.value = n

    def get_partial_selection(self):
        return self.get_processor("Select Partial Band").intProperty.value

    def modify_network(self, hdf5_path, hdf5_outport, xpos, ypos):
        self.network.lock()
        # Remove default hdf5 to function section.
        self.remove_processor('ChildCollector')
        self.remove_processor('h5ToFunction')
        self.remove_processor('dataFrame')
        pathSelection = self.get_processor('PathSelection')

        with h5py.File(hdf5_path,"r") as h5:
            total_list = []
            for key in h5["/DOS/Total"].keys():
                if key == "Energy": continue
                total_list.append(key)
            total_list.sort(key=lambda item: "".join(reversed(item)))
            down_totals = [x for x in total_list if x.endswith("(dwn)")]
            up_totals = [x for x in total_list if x.endswith("(up)")]

            has_partial = "/DOS/Partial" in h5
            if has_partial:
                n_partials = len(h5['/DOS/Partial'])
                partial_list = []
                for key in h5["/DOS/Partial/0"]:
                    if key == "Energy": continue
                    partial_list.append(key)
                    partial_list.sort(key=lambda item: "".join(reversed(item)))
                    down_partials = [x for x in partial_list if x.endswith("(dwn)")]
                    up_partials = [x for x in partial_list if x.endswith("(up)")]


        to_func_processors = []

        # Setup totals
        totalSelection = self.add_processor("org.inviwo.hdf5.PathSelection", "Select Total", xpos+7, ypos)
        self.network.addConnection(pathSelection.getOutport('outport'), totalSelection.getInport('inport'))

        totalCollector = self.add_processor("org.inviwo.DataFrameCollector", "TotalCollector", xpos+7, ypos+15)

        xpos_tmp = xpos + 7
        for n, key in enumerate(down_totals):
            toFunction = self.add_processor("org.inviwo.HDF5ToFunction", key, xpos_tmp, ypos+6)
            to_func_processors.append(toFunction)
            self.network.addConnection(totalSelection.getOutport('outport'), toFunction.getInport('hdf5HandleFlatMultiInport'))
            toFunction.yNamePrependParentsProperty.value = 1

            addOperation = self.add_processor("org.inviwo.FunctionOperationNary", "Total Down Add {}".format(n), xpos_tmp, ypos+9)
            self.network.addConnection(toFunction.getOutport("functionVectorOutport"), addOperation.getInport("functionFlatMultiInport"))
            addOperation.operationProperty.value = 'add'

            negateOperation = self.add_processor("org.inviwo.FunctionOperationUnary", "Total Down Negate {}".format(n), xpos_tmp, ypos+12)
            self.network.addConnection(addOperation.getOutport("dataframeOutport"), negateOperation.getInport("dataframeInport"))
            self.network.addConnection(negateOperation.getOutport("dataframeOutport"), totalCollector.getInport('dataframeMultiInport'))
            negateOperation.operationProperty.value = 'negate'
        
            n += 1
            xpos_tmp += 7

        for n, key in enumerate(up_totals):
            toFunction = self.add_processor("org.inviwo.HDF5ToFunction", key, xpos_tmp, ypos+6)
            to_func_processors.append(toFunction)
            self.network.addConnection(totalSelection.getOutport('outport'), toFunction.getInport('hdf5HandleFlatMultiInport'))
            toFunction.yNamePrependParentsProperty.value = 1

            addOperation = self.add_processor("org.inviwo.FunctionOperationNary", "Total Up Add {}".format(n), xpos_tmp, ypos+9)
            self.network.addConnection(toFunction.getOutport("functionVectorOutport"), addOperation.getInport("functionFlatMultiInport"))
            self.network.addConnection(addOperation.getOutport("dataframeOutport"), totalCollector.getInport('dataframeMultiInport'))
            addOperation.operationProperty.value = 'add'
            
            n += 1
            xpos_tmp += 7

        # Setup partials
        partialSelection = self.add_processor("org.inviwo.hdf5.PathSelection", "Select Partial", xpos_tmp, ypos)
        partialBandSelection = self.add_processor("org.inviwo.HDF5PathSelectionInt", "Select Partial Band", xpos_tmp, ypos+3)
        self.network.addConnection(pathSelection.getOutport('outport'), partialSelection.getInport('inport'))
        self.network.addConnection(partialSelection.getOutport('outport'), partialBandSelection.getInport('hdf5HandleInport'))

        partialBandSelection.intProperty.value = 0
        partialBandSelection.intProperty.minValue = 0
        partialBandSelection.intProperty.maxValue = n_partials


        partialCollector = self.add_processor("org.inviwo.DataFrameCollector", "PartialCollector", xpos_tmp, ypos+15)

        
        for n, key in enumerate(down_partials):
            toFunction = self.add_processor("org.inviwo.HDF5ToFunction", key, xpos_tmp, ypos+6)
            to_func_processors.append(toFunction)
            self.network.addConnection(partialBandSelection.getOutport('hdf5HandleVectorOutport'), toFunction.getInport('hdf5HandleFlatMultiInport'))
            toFunction.yNamePrependParentsProperty.value = 2

            addOperation = self.add_processor("org.inviwo.FunctionOperationNary", "Partial Down Add {}".format(n), xpos_tmp, ypos+9)
            self.network.addConnection(toFunction.getOutport("functionVectorOutport"), addOperation.getInport("functionFlatMultiInport"))
            addOperation.operationProperty.value = 'add'

            negateOperation = self.add_processor("org.inviwo.FunctionOperationUnary", "Partial Down Negate {}".format(n), xpos_tmp, ypos+12)
            self.network.addConnection(addOperation.getOutport("dataframeOutport"), negateOperation.getInport("dataframeInport"))
            self.network.addConnection(negateOperation.getOutport("dataframeOutport"), partialCollector.getInport('dataframeMultiInport'))
            negateOperation.operationProperty.value = 'negate'
            
            n += 1
            xpos_tmp += 7

        for n, key in enumerate(up_partials):
            toFunction = self.add_processor("org.inviwo.HDF5ToFunction", key, xpos_tmp, ypos+6)
            to_func_processors.append(toFunction)
            self.network.addConnection(partialBandSelection.getOutport('hdf5HandleVectorOutport'), toFunction.getInport('hdf5HandleFlatMultiInport'))
            toFunction.yNamePrependParentsProperty.value = 2

            addOperation = self.add_processor("org.inviwo.FunctionOperationNary", "Partial Up Add {}".format(n), xpos_tmp, ypos+9)
            self.network.addConnection(toFunction.getOutport("functionVectorOutport"), addOperation.getInport("functionFlatMultiInport"))
            self.network.addConnection(addOperation.getOutport("dataframeOutport"), partialCollector.getInport('dataframeMultiInport'))
            addOperation.operationProperty.value = 'add'
            
            n += 1
            xpos_tmp += 7

        collector = self.add_processor("org.inviwo.DataFrameCollector", "Collector", xpos+7, ypos+18)
        self.network.addConnection(totalCollector.getOutport("dataframeOutport"), collector.getInport('dataframeMultiInport'))
        self.network.addConnection(partialCollector.getOutport("dataframeOutport"), collector.getInport('dataframeMultiInport'))

        linePlot = self.get_processor("LinePlot")
        self.network.addConnection(collector.getOutport("dataframeOutport"), linePlot.getInport('dataFrameInport'))

        self.network.unlock()
        # Set hdf5 selector paths
        pathSelection.selection.value = '/DOS'
        totalSelection.selection.value = '/Total'
        partialSelection.selection.value = '/Partial'
        # Set function paths.
        self.network.lock() # Lock network for performence increase.
        names = down_totals + up_totals + down_partials + up_partials
        for i, toFunction in enumerate(to_func_processors):
            toFunction.implicitXProperty.value = False
            toFunction.xPathSelectionProperty.value = '/Energy'
            toFunction.yPathSelectionProperty.value = '/{}'.format(names[i])
            toFunction.xPathFreeze.value = True
            toFunction.yPathFreeze.value = True
        self.set_y_selection_type(2)
        self.network.unlock()
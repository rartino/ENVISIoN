import inviwopy
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
import inviwopy.glm as glm

class Subnetwork():
    def __init__(self, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.processors = {}

        self.decoration_inport = None # Should be defined if subnetwork can use decorations.
        self.decoration_outport = None # Should be defined if subnetwork can be used as decoration.
        self.decoration_outports = []
        self.decoration_mergers = []
        self.last_inport = None

    def hide(self):
        raise EnvisionError('Subnetwork needs to have a hide function overloaded.')

    def show(self):
        raise EnvisionError('Subnetwork needs to have a show function overloaded.')

    def disconnect_decorations_port(self, deco_outport):
        # Remove a decoration from this visualisaiton.
        
        # Clear ports and image mergers.
        for port in self.decoration_outports:
            self.network.removeConnection(port, self.decoration_inport)
        while len(self.decoration_mergers) > 0:
            identifier = self.decoration_mergers[0].identifier
            del self.decoration_mergers[0]
            self.remove_processor(identifier)

        # Remove wanted decoration port.
        self.decoration_outports.remove(deco_outport)

        # Reconnect remaining decorations.
        self.last_inport = self.decoration_inport
        for port in self.decoration_outports:
            self.connect_decoration_ports(port)
        

    def connect_decoration_ports(self, deco_outport):
        if self.decoration_inport == None:
            raise EnvisionError("Tried to connect decorations to incompatible visualisation.")
        if self.last_inport == None:
            self.last_inport = self.decoration_inport
        if deco_outport in self.decoration_outports:
            raise EnvisionError('Decoration already connected.')
        
        # Connect decoration directly
        if len(self.decoration_outports) == 0:
            self.network.addConnection(deco_outport, self.decoration_inport)
        # Add image mergers to merge all decorations.
        else:
            self.network.removeConnection(self.decoration_outports[-1], self.last_inport)
            decorationMerger = self.add_processor('org.inviwo.ImageCompositeProcessorGL', 'DecorationMerger', len(self.decoration_outports) * 7, -3)
            self.decoration_mergers.append(decorationMerger)
            self.network.addConnection(self.decoration_outports[-1], decorationMerger.getInport('imageInport1'))
            self.network.addConnection(deco_outport, decorationMerger.getInport('imageInport2'))
            self.network.addConnection(decorationMerger.getOutport('outport'), self.last_inport)
            self.last_inport = decorationMerger.getInport('imageInport2')

        self.decoration_outports.append(deco_outport)

    def add_processor(self, id, name, xpos=0, ypos=0):
        # Add a processor. If processor with name already added return it.
        if name in self.processors:
            return self.processors[name]
        factory = self.app.processorFactory
        new_processor = factory.create(id, glm.ivec2(xpos*25, ypos*25))
        new_processor.identifier = name
        self.network.addProcessor(new_processor)

        self.processors[name] = new_processor
        return new_processor

    def remove_processor(self, id):
        # Processor python reference has to be deleted before
        # processor is deleted in inviwo, risk crash otherwise
        identifier = self.get_processor(id).identifier
        del self.processors[id]
        self.network.removeProcessor(self.network.getProcessorByIdentifier(identifier))

    def remove_processor_by_ref(self, processor):
        self.remove_processor(processor.identifier)
            # self.processors = {key:val for key, val in self.processors.items() if val != processor}
            # self.network.removeProcessor(processor)

    def get_processor(self, id):
        if id in self.processors:
            return self.processors[id]
        raise ProcessorNotFoundError("Processor with ID " + id + " not found.")

    def clear_processors(self):
        for key in list(self.processors.keys()):
            self.remove_processor(key)
        del self.processors

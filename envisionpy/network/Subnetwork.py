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

        self.decorations = []
        self.decoration_mergers = []
        self.decoration_inport = None
        self.camera_prop = None

    def disconnect_3d_decoration(self, image_outport):
        # TODO:
        # remove connections
        # remove image mergers if needed
        # remove from list 
        pass

    def connect_3d_decoration(self, image_outport, camera_prop=None):
        # Should be overloaded in inheriting subnetwork class.
        if self.decoration_inport == None:
            raise ProcessorNetworkError("Tried to connect decorations to incompatible visualisation.")
        if image_outport in self.decorations:
            return
        
        if len(self.decorations) == 0:
            self.network.addConnection(image_outport, self.decoration_inport)

        # Add image mergers to merge all decorations.
        else:
            self.network.removeConnection(self.decorations[-1], self.decoration_inport)
            decorationMerger = self.add_processor('org.inviwo.ImageCompositeProcessorGL', 'DecorationMerger', len(self.decorations) * 7, -3)
            self.decoration_mergers.append(decorationMerger)
            self.network.addConnection(self.decorations[-1], decorationMerger.getInport('imageInport1'))
            self.network.addConnection(image_outport, decorationMerger.getInport('imageInport2'))
            self.network.addConnection(decorationMerger.getOutport('outport'), self.decoration_inport)
            self.decoration_inport = decorationMerger.getInport('imageInport2')
        self.decorations.append(image_outport)

        # Link camera properties.
        if camera_prop != None and camera_prop != self.camera_prop:
            self.network.addLink(self.camera_prop, camera_prop)

    def add_processor(self, id, name, xpos=0, ypos=0):
        factory = self.app.processorFactory
        new_processor = factory.create(id, glm.ivec2(xpos*25, ypos*25))
        new_processor.identifier = name
        self.network.addProcessor(new_processor)

        self.processors[name] = new_processor
        return new_processor

    def remove_processor(self, id):
        self.network.removeProcessor(self.processors[id])
        del self.processors[id]

    def remove_processor_by_ref(self, processor):
            self.processors = {key:val for key, val in self.processors.items() if val != processor}
            self.network.removeProcessor(processor)

    def get_processor(self, id):
        if id in self.processors:
            return self.processors[id]
        raise ProcessorNotFoundError("Processor with ID " + id + " not found.")

    def clear_processors(self):
        for key in list(self.processors.keys()):
            self.remove_processor(key)
        del self.processors

#
#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys,os,inspect
from envisionpy.utils.exceptions import *

# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# sys.path.insert(0, os.path.expanduser(path_to_current_folder))

import inviwopy.glm as glm

# TODO: Have each NetworkHandler instance manage their own processors.
#       Separate clear functions for only owned processors and all processors.

# TODO: Manage canvases better.

class NetworkHandler():
    """ Base class for managing an inviwo network.

    """
    def __init__(self, inviwoApp):
        self.app = inviwoApp
        self.network = inviwoApp.network
        if not hasattr(self, "processors"):
            self.processors = {}
        # self.canvases = []

    def get_ui_data(self):
        raise EnvisionError("get_ui_data must be overloaded in subclasses before using.")

    def clear_processors(self):
    # Remove all the processors associated with this handler.
        for id in tuple(self.processors):
            self.remove_processor(id)

    def add_processor(self, id, name, xpos=0, ypos=0):
        factory = self.app.processorFactory
        new_processor = factory.create(id, glm.ivec2(xpos, ypos))
        new_processor.identifier = name
        self.network.addProcessor(new_processor)

        self.processors[name] = new_processor
        # self.processors.append(new_processor)
        return new_processor

    def remove_processor(self, id):
        self.network.removeProcessor(self.processors[id])
        del self.processors[id]

    def remove_processor_by_ref(self, processor):
        self.network.removeProcessor(processor)
        self.processors = {key:val for key, val in self.processors.items() if val != processor}

    def get_processor(self, id):
        if id in self.processors:
            return self.processors[id]
        raise ProcessorNotFoundError("Processor with ID " + id + " not found.")
        # return None

    def add_h5source(self, h5file, xpos=0, ypos=0):
        name = os.path.splitext(os.path.basename(h5file))[0]
        try:
            processor = self.get_processor(name)
        except ProcessorNotFoundError:
            new_processor = self.add_processor('org.inviwo.hdf5.Source', name, xpos, ypos)
            filename = new_processor.getPropertyByIdentifier('filename')
            filename.value = h5file
            processor = new_processor
        return processor

    def add_property(self, id, name, processor):
        factory = self.app.propertyFactory
        new_property = factory.create(id)
        new_property.identifier = name
        processor.addProperty(new_property, name)
        return new_property

    

    def position_canvases(self, x, y):
    # Updates the position of the canvases
    # Upper left corner will be at coordinate (x, y)
        canvases = []
        try: canvases.append(self.get_processor("Canvas"))
        except ProcessorNotFoundError: pass
        try: canvases.append(self.get_processor("SliceCanvas"))
        except ProcessorNotFoundError: pass
        try: canvases.append(self.get_processor("Unit Cell Canvas"))
        except ProcessorNotFoundError: pass
        try: canvases.append(self.get_processor("graphCanvas"))
        except ProcessorNotFoundError: pass
        print("CANVASES____")
        print(canvases)
        for canvas in canvases:
            canvas.position.value = glm.ivec2(x, y)
            # x += canvas.inputSize.dimensions.value.x
            y += canvas.inputSize.dimensions.value.y

        # volumeCanvas.position.value = inviwopy.glm.ivec2(x, y)
        # if sliceCanvas:
        #     sliceCanvas.position.value = inviwopy.glm.ivec2(x, y + volumeCanvas.inputSize.dimensions.value.y + 50)
        # if unitcellCanvas:
        #     unitcellCanvas.position.value = inviwopy.glm.ivec2(x + volumeCanvas.inputSize.dimensions.value.x, y)

    # def position_canvases(self, x, y):
    # # Updates the position of the canvases
    # # Upper left corner will be at coordinate (x, y)
    #     network = inviwopy.app.network
    #     sliceCanvas = network.getProcessorByIdentifier('SliceCanvas')
    #     volumeCanvas = network.getProcessorByIdentifier('Canvas')
    #     if not volumeCanvas:
    #         return
    #     volumeCanvas.position.value = inviwopy.glm.ivec2(x, y)
    #     if not sliceCanvas:
    #         return
    #     sliceCanvas.position.value = inviwopy.glm.ivec2(x, y + volumeCanvas.inputSize.dimensions.value.y + 50)

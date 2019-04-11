#
#  ENVISIoN
#
#  Copyright (c) 2017 Josef Adamsson
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
import inviwopy.glm as glm
import os

app = inviwopy.app
network = app.network

def _add_processor(id,name,xpos=0,ypos=0):
    factory = app.processorFactory
    new_processor = factory.create(id, glm.ivec2(xpos, ypos))
    new_processor.identifier = name
    network.addProcessor(new_processor)
    return new_processor

def _add_h5source(h5file, xpos=0, ypos=0):
    name = os.path.splitext(os.path.basename(h5file))[0]
    processor = network.getProcessorByIdentifier(name)
    print('9')
    if processor is None:
        new_processor = _add_processor('org.inviwo.hdf5.Source', name, xpos, ypos)
        filename = new_processor.getPropertyByIdentifier('filename')
        filename.value = h5file
        processor = new_processor

    return processor

def _add_property(id, name, processor):
    print('10')
    factory = app.propertyFactory
    new_property = factory.create(id)
    new_property.identifier = name
    processor.addProperty(new_property, name)
    return new_property


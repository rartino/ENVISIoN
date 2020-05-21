import os, sys, inspect, inviwopy
import inviwopy.glm as glm
app = inviwopy.app
network = app.network
factory = app.processorFactory
network.clear()

"""
test_processor = factory.create('org.inviwo.TestProcessor', glm.ivec2(0,0))

old_init = test_processor.initializeResources

def new_init():
    old_init()
    print("san")

test_processor.initializeResources = new_init

network.addProcessor(test_processor)
"""
"""
test_processor = factory.create('org.inviwo.CanvasGL', glm.ivec2(0,0))

network.addProcessor(test_processor)
"""

help(inviwopy)
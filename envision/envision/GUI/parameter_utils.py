 
#   Inviwo - Interactive Visualization Workshop
 
#   Copyright (c) 2014-2019 Inviwo Foundation, Jesper Ericsson
#   All rights reserved.
 
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
 
#   1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
 
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#   ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
import sys, os

sys.path.insert(0, os.path.expanduser("C:/ENVISIoN/envision/"))

import inviwopy
import inspect
import envision
import envision.inviwo
app = inviwopy.app
network = app.network


def clear_processor_network():
    network.clear()

def disable_visualization(type):
    # Disable the canvas of specified visualization
    pass

def enable_visualization(type, path):
    # Build specified network or enable canvas if already exists
    if type == 'Charge':
        start_charge_vis(path)
    

def set_hd5_source(path):
    # set the hdf5 source of all active visualizations
    # maybe close those who are not compatible?
    pass

# -------------------
# --Charge specific--

def start_charge_vis(path, iso = None, slice = False):
    # Start the charge visualization

    # TODO: if charge network exists, only enable the canvas

    network.clear()
    envision.inviwo.charge(path, iso = None, slice = False, xpos = 0, ypos = 0)

#--Transfer function editing--

def charge_add_tf_point(value, color):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.add(value, color)

def charge_clear_tf():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.clear()

def charge_remove_tf_point(index):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    if len(charge_get_points()) <= index:
        print("No points to remove")
        return
    point_to_remove = tf_property.getValueAt(0)
    tf_property.remove(point_to_remove)


def charge_get_points():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    return [[x.pos, x.color] for x in tf_property.getValues()]

#--Background and lighting--

def charge_set_shading_mode(mode):
    pass

def charge_set_background(color_1 = None, color_2 = None, style = 2):
    pass

def charge_toggle_plane(enable):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    pos_indicator = Raycaster.positionindicator
    pos_indicator.plane1.enable.value = True
    pos_indicator.plane2.enable.value = False
    pos_indicator.plane3.enable.value = False
    pos_indicator.enable.value = enable

def charge_set_plane_normal(x, y, z):
    #Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    #plane = Raycaster.positionindicator.plane1
    #plane.normal.value = inviwopy.glm.vec3(x, y, z)

    vol_slice = network.getProcessorByIdentifier('Volume Slice')
    vol_slice.sliceAxis.value = 3
    vol_slice.planeNormal.value = inviwopy.glm.vec3(x, y, z)


def charge_set_plane_height(h):
    pass

POINT: ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'color', 'pos']

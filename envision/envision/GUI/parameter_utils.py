 
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
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/../../'))

import inviwopy
import inspect
import envision
import envision.inviwo
app = inviwopy.app
network = app.network

# TODO: make better visualization intialization code

def clear_processor_network():
    network.clear()

def disable_visualization(type):
    # Disable the canvas of specified visualization
    pass

def enable_visualization(type, path):
    # Build specified network or enable canvas if already exists
    if type == 'Charge':
        start_charge_vis(path,False)
    
def set_canvas_position(position = None, type='Canvas'):
    #Change the canvas-position
    Canvas = network.getProcessorByIdentifier(type)
    if position != None:
        Canvas.position.value = position

def set_unitcell_canvas_position(position = None):
    #Change the canvas-position
    Canvas = network.getProcessorByIdentifier('Unit Cell Canvas')
    if position != None:
        Canvas.position.value = position

def set_dos_canvas_position(position = None):
    #Change the canvas-position
    Canvas = network.getProcessorByIdentifier('DOS Canvas')
    if position != None:
        Canvas.position.value = position
    for n in range(2,5):
        position = position + 20
        Canvas = network.getProcessorByIdentifier('DOS Canvas'+str(n))
        if position != None:
            Canvas.position.value = position
    else:
        pass


def set_hd5_source(path):
    # set the hdf5 source of all active visualizations
    # maybe close those who are not compatible?
    pass

# -------------------
# --Charge specific--

def start_charge_vis(path,isSlice):
    # Start the charge visualization
    # Hdf5 needs to be charge and unitcell-parsed
    envision.inviwo.charge(path, 
                                iso = None, slice = isSlice, 
                                xpos = 0, ypos = 0)
    charge_clear_tf()
    charge_toggle_plane(isSlice)
    if isSlice:
        charge_set_plane_normal()
        charge_set_background(inviwopy.glm.vec4(1,1,1,1),
                            inviwopy.glm.vec4(0,0,0,1),3,0,'SliceBackground')
        

    # TODO: if charge network exists, only enable the canvas
"""
    network.clear()
    envision.parser.vasp.unitcell(path, "/home/labb/VASP_files/NaCl_charge_density")
    envision.parser.vasp.charge(path, "/home/labb/VASP_files/NaCl_charge_density")
    envision.inviwo.unitcell(path, 0)
    envision.inviwo.charge(path, iso = None, slice = True, xpos = -600, ypos = 0)
    charge_set_plane_height(2)
    charge_toggle_plane(True)"""

def charge_set_slice(enable):
    # Toggle slice visualisation on or off
    charge_toggle_plane(enable)
    SliceCanvas = network.getProcessorByIdentifier('SliceCanvas')
    SliceCanvas

#--Transfer function editing--

def charge_set_mask(maskMin, maskMax):
# Set the mask of the transfer function
# Only values between maskMin and maskMax are visible
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    print(tf_property.mask)
    tf_property.setMask(maskMin, maskMax)
    print(tf_property.mask)
    # vec2 = inviwopy.glm.dvec2(min, max)
    # print(vec2)
    # tf_property.mask = vec2


def charge_add_tf_point(value, color):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.add(value, color)

    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    if VolumeSlice:
        VolumeSlice.tfGroup.transferFunction.value = tf_property.value

def charge_clear_tf():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    print(dir(tf_property.mask))
    tf_property.clear()

    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    if VolumeSlice:
        VolumeSlice.tfGroup.transferFunction.value = tf_property.value

def charge_remove_tf_point(index):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    if len(charge_get_points()) <= index:
        print("No points to remove")
        return
    point_to_remove = tf_property.getValueAt(index)
    tf_property.remove(point_to_remove)

    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    if VolumeSlice:
        VolumeSlice.tfGroup.transferFunction.value = tf_property.value


def charge_get_points():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    return [[x.pos, x.color] for x in tf_property.getValues()]

#--Background and lighting--

def charge_set_shading_mode(mode):
    Raycaster = network.getProcessorByIdentifier('Volume Slice')
    Raycaster.lighting.shadingMode.value = mode
    pass

def charge_set_background(color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None, type = 'Background'):
    Background = network.getProcessorByIdentifier(type)
    if styleIndex != None:
        Background.backgroundStyle.selectedIndex = styleIndex
    if color_1 != None:
        Background.bgColor1.value = color_1
    if color_2 != None:
        Background.bgColor2.value = color_2
    if blendModeIndex != None:
        Background.blendMode.selectedIndex = blendModeIndex

# --Slice planes--

def charge_toggle_plane(enable):
# Set if the slice plane should be visible in the volume
# TODO: remove plane.enable.value, move to some initialization code
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    pos_indicator = Raycaster.positionindicator
    pos_indicator.plane1.enable.value = True
    pos_indicator.plane2.enable.value = False
    pos_indicator.plane3.enable.value = False
    pos_indicator.enable.value = enable

def charge_set_plane_normal(x=0, y=1, z=0):
# Set the normal of the slice plane
# x, y, and z can vary between 0 and 1
# TODO: move sliceAxis.value to some initialization code
    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    VolumeSlice.sliceAxis.value = 3
    VolumeSlice.planeNormal.value = inviwopy.glm.vec3(x, y, z)

def charge_set_plane_height(height):
# Set the height of the volume slice plane
# Height can vary between 0 and 1.
    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')

    # Create position vector based on plane normal 
    normal = VolumeSlice.planeNormal.value
    xHeight = normal.x * height
    yHeight = normal.y * height
    zHeight = normal.z * height
    VolumeSlice.planePosition.value = inviwopy.glm.vec3(xHeight, yHeight, zHeight)

    



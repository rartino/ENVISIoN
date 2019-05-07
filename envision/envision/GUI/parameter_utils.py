 
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
##############################################################################################
#
#  Alterations to this file by Anton Hjert
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
 
import sys, os
import inspect
path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir+'/../../'))
import h5py
import numpy
from matplotlib import pyplot as plt 
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

def change_scale(scaleValue,processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    if dataProcessor:
        dataProcessor.scale.value = scaleValue

def get_scale(processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    if dataProcessor:
        return dataProcessor.scale.value

def set_all_data(processor='',setAll=True):
    dataProcessor = network.getProcessorByIdentifier(processor)
    if dataProcessor:
        dataProcessor.allYSelection.value = setAll

def get_x_range(type='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(type)
    return dataProcessor.x_range.value

def get_y_range(type='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(type)
    return dataProcessor.y_range.value

def set_x_range(value, type, processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    print('xrange')
    if type == 'min':
        dataProcessor.x_range.value = inviwopy.glm.vec2(dataProcessor.x_range.value[0],value)
    else:
        dataProcessor.x_range.value = inviwopy.glm.vec2(value, dataProcessor.x_range.value[1])

def set_y_range(value, type, processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    if type == 'min':
        dataProcessor.y_range.value = inviwopy.glm.vec2(dataProcessor.y_range.value[0],value)
    else:
        dataProcessor.y_range.value = inviwopy.glm.vec2(value, dataProcessor.y_range.value[1])

def enable_help_line(setLine=False, type='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(type)
    dataProcessor.enable_line.value = setLine

def set_help_line(value, type='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(type)
    dataProcessor.line_x_coordinate.value = value

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
        position = position + 20
        Canvas = network.getProcessorByIdentifier('DOS Canvas2')
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
    clear_processor_network()
    envision.inviwo.charge(path, 
                                iso = None, slice = isSlice, 
                                xpos = 0, ypos = 0)
    charge_clear_tf()
    charge_toggle_plane(isSlice)
    if isSlice:
        charge_set_plane_normal()
        charge_set_background(inviwopy.glm.vec4(0,0,0,1),
                            inviwopy.glm.vec4(1,1,1,1),3,0,'SliceBackground')
    slice_copy_tf()
        

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
    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    if VolumeSlice:
        VolumeSlice.tfGroup.transferFunction.setMask(maskMin,maskMax)
    # vec2 = inviwopy.glm.dvec2(min, max)
    # print(vec2)
    # tf_property.mask = vec2

def show_volume_dist(path_to_hdf5):
    volume = network.getProcessorByIdentifier('HDF5 To Volume')
    with h5py.File(path_to_hdf5,"r") as h5:
        data = h5[volume.volumeSelection.value].value
        result = []
        [ result.extend(el) for el in data[0] ]
        newResult = []
        [ newResult.append((element + abs(min(result)))/(max(result) + abs(min(result)))) \
            for element in result ]
        dataList= numpy.array(newResult)
        plt.hist(dataList,bins=200, density = True)
        plt.title("TF and ISO data") 
        plt.show()

def show_canvas(show=True,type='Canvas'):
    canvas = network.getProcessorByIdentifier(type)
    canvas.meta.visible = show

def charge_add_tf_point(value, color):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.add(value, color)
    slice_copy_tf()

def slice_copy_tf():
    VolumeSlice = network.getProcessorByIdentifier('Volume Slice')
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    if VolumeSlice:
        VolumeSlice.tfGroup.transferFunction.value = tf_property.value
        #VolumeSlice.tfGroup.transferFunction.add(0.0, inviwopy.glm.vec4(0.0, 0.0, 0.0, 1.0))
        #VolumeSlice.tfGroup.transferFunction.add(1.0, inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))
        tf_points = charge_get_points()
        if len(tf_points) > 0:
            VolumeSlice.tfGroup.transferFunction.add(0.99*tf_points[0][0], inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))

def charge_clear_tf():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    print(dir(tf_property.mask))
    tf_property.clear()
    slice_copy_tf()

def charge_remove_tf_point(index):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    if len(charge_get_points()) <= index:
        print("No points to remove")
        return
    point_to_remove = tf_property.getValueAt(index)
    tf_property.remove(point_to_remove)
    slice_copy_tf()


def charge_get_points():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    return [[x.pos, x.color] for x in tf_property.getValues()]

#--Background and lighting--

def charge_set_shading_mode(mode):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
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

    



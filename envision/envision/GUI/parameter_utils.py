#
#  ENVISIoN
#
#  Copyright (c) 2019 Jesper Ericsson
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

def clear_processor_network():
    network.clear()

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

def get_x_range(processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    return dataProcessor.x_range.value

def get_y_range(processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
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

def enable_help_line(setLine=False, processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    dataProcessor.enable_line.value = setLine

def set_help_line(value, processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    dataProcessor.line_x_coordinate.value = value

def get_help_line(processor='Line plot'):
    dataProcessor = network.getProcessorByIdentifier(processor)
    if dataProcessor:
        return dataProcessor.line_x_coordinate.value

def set_canvas_position(position = None, processor='Canvas'):
    #Change the canvas-position
    Canvas = network.getProcessorByIdentifier(processor)
    if position != None:
        Canvas.position.value = position

def enable_label(xLabel = None, yLabel = None, processor = "Line plot"):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if xLabel != None:
            plotter.show_x_labels.value = xLabel
        if yLabel != None:
            plotter.show_y_labels.value = yLabel

def isEnabled_label(processor = "Line plot"):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return [plotter.show_x_labels.value,plotter.show_y_labels.value]

def enable_grid(gridBool = None, processor="Line plot"):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if gridBool != None:
            plotter.enable_grid.value = gridBool

def set_grid(value=None,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if value != None:
            plotter.grid_width.value = value

def get_grid(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.grid_width.value

def get_label(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.label_number.value

def set_label(value=None,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if value != None:
            plotter.label_number.value = value
        

def isEnable_grid(processor="Line plot"):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.enable_grid.value

def enable_multiple_y(multipleBool=None,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if multipleBool != None:
            plotter.boolYSelection.value = multipleBool

def isEnabled_multiple_y(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.boolYSelection.value

def enable_all_y(multipleBool=None,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        if multipleBool != None:
            plotter.allYSelection.value = multipleBool

def isEnabled_all_y(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.allYSelection.value

def get_yline_range(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.groupYSelection_.value
    
def set_yline_range(option=1,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        plotter.groupYSelection_.value = option

def get_partial_value(processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        return plotter.intProperty.value
    
def set_partial_value(option=1,processor='Line plot'):
    plotter = network.getProcessorByIdentifier(processor)
    if plotter:
        plotter.intProperty.value = option


    



##  ENVISIoN
##
##  Copyright (c) 2021 Gabriel Anderberg, Didrik Axén,  Adam Engman,
##  Kristoffer Gubberud Maras, Joakim Stenborg
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice, this
##  list of conditions and the following disclaimer.
##  2. Redistributions in binary form must reproduce the above copyright notice,
##  this list of conditions and the following disclaimer in the documentation
##  and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
##  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## ##############################################################################################

from envisionpy.utils.exceptions import *
import inviwopy.glm as glm
import h5py
import numpy as np
from .AtomPositions import AtomPositions
from .PartialChargeDensity import PartialChargeDensity
from .ChargeDensity import ChargeDensity
from .ELFVolume import ELFVolume
from .FermiSurface import FermiSurface
from .Bandstructure import Bandstructure
from .DensityOfStates import DensityOfStates
from .MultiVolume import MultiVolume
from .baseNetworks.Decoration import Decoration
from .ForceVectors import ForceVectors
from .MolecularDynamics import MolecularDynamics
from envisionpy.processor_network import PCFNetworkHandler
from envisionpy.processor_network import Bandstructure3DNetworkHandler
from envisionpy.processor_network import BandstructureNetworkHandler
from .Test import Test

class VisualisationManager():
    '''
    Class for managing one visualisation instance from a single HDF5 file.
    '''
    def __init__(self, hdf5_path, inviwoApp, inviwo = True):
        print("Initialising VisMan")
        self.app = inviwoApp
        self.network = inviwoApp.network
        self.subnetworks = {}
        self.decorations = {}
        self.inviwo = inviwo
        self.main_vis_type = None
        self.available_visualisations = []

        self.hdf5_path = hdf5_path

        # Add hdf5 source processor
        self.hdf5Source = self.app.processorFactory.create('org.inviwo.hdf5.Source', glm.ivec2(0, 0))
        self.hdf5Source.filename.value = hdf5_path
        self.network.addProcessor(self.hdf5Source)
        self.hdf5Output = self.hdf5Source.getOutport('outport')

        # Check what visualisations are possible with this hdf5-file.
        with h5py.File(hdf5_path, 'r') as file:
            if ChargeDensity.valid_hdf5(file):
                self.available_visualisations.append("charge")
            if ELFVolume.valid_hdf5(file):
                self.available_visualisations.append("elf")
            if BandstructureNetworkHandler.valid_hdf5(file):
                self.available_visualisations.append("band2d")
            if Bandstructure3DNetworkHandler.valid_hdf5(file):
                self.available_visualisations.append("band3d")
            if AtomPositions.valid_hdf5(file):
                self.available_visualisations.append("atom")
            if FermiSurface.valid_hdf5(file):
                self.available_visualisations.append("fermi")
            if PartialChargeDensity.valid_hdf5(file):
                self.available_visualisations.append("parchg")
            if Bandstructure.valid_hdf5(file):
                self.available_visualisations.append("band")
            if DensityOfStates.valid_hdf5(file):
                self.available_visualisations.append("dos")
            if PCFNetworkHandler.valid_hdf5(file):
                self.available_visualisations.append("pcf")
            if ForceVectors.valid_hdf5(file):
                self.available_visualisations.append("force")
            if MolecularDynamics.valid_hdf5(file):                           #MD
                self.available_visualisations.append("molecular_dynamics")
            #Det här behöver ändras från Test.valid_hdf5 till force.valid_hdf5
            #och animation.valid_hdf5
        #    if Test.valid_hdf5(file):
        #        self.available_visualisations.append("force")
        #        self.available_visualisations.append("moldyn")
            if len(set(['charge', 'elf', 'fermi', 'parchg']) & set(self.available_visualisations)) > 0:
                self.available_visualisations.append('multi')
### Legacy information about old ENVISON GUI, add appendix in användarmanual, teknisk doku,
### Ta bort installationssteg som är kopplat till gamla GUI
### Add legacy instruction at end of readme.rst
###
    def start(self, vis_type, bool = True, *args):
        # Start a new main visualisation.
        subnetwork = self.get_subnetwork(vis_type, bool, *args)
        # Decoration visualisation.
        if issubclass(type(subnetwork), Decoration):
            self.decorations[vis_type] = subnetwork
            for other_type, other_network in self.subnetworks.items():
                if other_type in subnetwork.valid_visualisations():
                    subnetwork.connect_decoration(other_network, other_type)
            subnetwork.show()
        elif vis_type in ['pcf', 'band2d', 'band3d']:
            pass
        # Normal visualisation.
        else:
            # Try to connect running decorations to this one.
            for deco_network in self.decorations.values():
                if vis_type in deco_network.valid_visualisations():
                    deco_network.connect_decoration(subnetwork, vis_type)
            subnetwork.show()
        # self.reset_canvas_positions()
        return subnetwork

    def stop(self, vis_type=None):

        if vis_type in ['band2d', 'band3d']:
            self.subnetworks[vis_type].stop_vis()
            print('Stopping: ' + vis_type)

        if vis_type == None:
            # Stop all visualisations and clear networks.
            for subnetwork in self.subnetworks:
                subnetwork.clear_processors()
            self.network.removeProcessor(self.hdf5Source)
            return

        if vis_type not in self.subnetworks:
            raise EnvisionError('Tried to stop non running visualisation.')
        if vis_type in self.decorations:
            del self.decorations[vis_type]
        self.subnetworks[vis_type].clear_processors()
        del self.subnetworks[vis_type]


    def get_subnetwork(self, vis_type, bool = True, *args):
        # Return the subnetwork for specified visualisation type.
        # If it does not exist, try to create it.

        if vis_type not in self.available_visualisations:
            raise EnvisionError('Cannot start visualisation ['+vis_type+'] with unsupported hdf5 file.')

        if vis_type in self.subnetworks:
            return self.subnetworks[vis_type]

        # Initialize a new subnetwork
        #Här behöver vi ändra subnetwork = ForceVectors(...) till subnetwork = Animation(...)
        #Ändra animation till molecular_dynamics
        if vis_type == "moldyn":
            subnetwork = ForceVectors(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
            #subnetwork = MolecularDynamics(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "pcf":
            subnetwork = PCFNetworkHandler(self.hdf5_path, self.app)

        elif vis_type == "band2d":
            subnetwork = BandstructureNetworkHandler(self.hdf5_path, self.app)

        elif vis_type == "band3d":
            subnetwork = Bandstructure3DNetworkHandler(self.hdf5_path, self.app)

        elif vis_type == "charge":
            subnetwork = ChargeDensity(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "elf":
            subnetwork = ELFVolume(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "force":
            subnetwork = ForceVectors(self.app, self.hdf5_path, self.hdf5Output, 0, 3, self.inviwo)

        elif vis_type == "molecular_dynamics":                                              #MD
            subnetwork = MolecularDynamics(self.app, self.hdf5_path, self.hdf5Output, 0, 3, self.inviwo)

        elif vis_type == "fermi":
            subnetwork = FermiSurface(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "parchg":
            subnetwork = PartialChargeDensity(self.app, self.hdf5_path, self.hdf5Output, 0, 3, *args)

        elif vis_type == "atom":
            subnetwork = AtomPositions(self.app, self.hdf5_path, self.hdf5Output, -20, 3)

        elif vis_type == "band":
            subnetwork = Bandstructure(self.app, self.hdf5_path, self.hdf5Output, 0, 3)

        elif vis_type == "dos":
            subnetwork = DensityOfStates(self.app, self.hdf5_path, self.hdf5Output, 0, 3)
        elif vis_type == "multi":
            subnetwork = MultiVolume(self.app, self.hdf5_path, self.hdf5Output, 30, 3)
            for t in ['charge', 'elf']:
                if t in self.subnetworks:
                    subnetwork.connect_volume(
                        self.subnetworks[t].volume_outport,
                        self.subnetworks[t].transfer_function_prop,
                        self.subnetworks[t].camera_prop)
        if vis_type not in ['pcf', 'band2d', 'band3d']:
            subnetwork.hide() # All new visualisations are hidden by default here.
        self.subnetworks[vis_type] = subnetwork
        return subnetwork

    def reset_canvas_positions(self, start_x=0, start_y=0, max_width=10000):
        # Position all canvases side by side starting with the upper right corner
        # in given start coordinate.
        x_tmp = start_x
        y_tmp = start_y
        for subnetwork in self.subnetworks.values():
            for canvas in subnetwork.canvases:
                if not canvas.widget.visibility: continue
                if x_tmp > start_x+max_width:
                    x_tmp = start_x
                    y_tmp += canvas.widget.dimensions[1]
                canvas.widget.position = glm.ivec2(x_tmp, y_tmp)
                x_tmp += canvas.widget.dimensions[0]


    def get_ui_data(self):
        data_packet = []
        data_packet.append(self.available_visualisations) # Available visualisations
        data_packet.append([]) # Active visualisations
        data_packet.append({}) # UI data for active visualisations.
        for vis_type, subnetwork in self.subnetworks.items():
            data_packet[1].append(vis_type)
            data_packet[2][vis_type] = subnetwork.get_ui_data()
        return data_packet

    def call_subnetwork(self, vis_type, function_name, param_list):
        if function_name not in dir(self.get_subnetwork(vis_type)):
            raise EnvisionError("Invalid function call")
        return getattr(self.get_subnetwork(vis_type), function_name)(*param_list)

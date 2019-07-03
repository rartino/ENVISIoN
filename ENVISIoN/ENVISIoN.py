#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys#,os,inspect
# path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append("/home/labb/Inviwo-latest/build/bin")
import inviwopy as ivw
import inviwopyapp as qt
import time

from processor_network.ChargeNetworkHandler import ChargeNetworkHandler
from processor_network.NetworkHandler import NetworkHandler
from processor_network.VolumeNetworkHandler import VolumeNetworkHandler

class ENVISIoN():
    """ Class for managing a inviwo instance 
        and running ENVISIoN visualizations with it.

        Acts as an interface to control all aspects of envision.

        Can be used by different interfaces as long as they send requests using
        the same JSON standard.
    """
    def __init__(self):
        self.initialize_inviwo_app()
        self.networkHandler = None

        
    def update(self):
        self.app.update()

    def initialize_inviwo_app(self):
        # Inviwo requires that a logcentral is created.
        self.lc = ivw.LogCentral()
        
        # Create and register a console logger
        self.cl = ivw.ConsoleLogger()
        self.lc.registerLogger(self.cl)

        # Create the inviwo application
        self.app = qt.InviwoApplicationQt()
        self.app.registerModules()

        # load a workspace
        # self.app.network.load(self.app.getPath(ivw.PathType.Workspaces) + "/boron.inv")

        # Make sure the app is ready
        self.app.update()
        self.app.waitForPool()
        self.app.update()
        self.app.network.clear()

    def handle_request(self, request):
        response = [request[0], False, "Unhandled request"]

        if request[0] == "start charge":
            response = self.start_charge_vis()
        elif request[0] == "stop vis":
            response = self.stop_visualization()
        
        return response
    
    # def start_visualisation(self, vis_type):
    #     if vis_type == "charge"

    def start_charge_vis(self):
        try:
            self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", self.app)
            return ["start charge", True, None] # TODO return if unitcell was found
        except AssertionError as error:
            return ["start charge", False, "Invalid HDF5 file"]

    def stop_visualization(self):
        if self.networkHandler:
            self.networkHandler.clear_processor_network()
            self.networkHandler = None
            return ["stop vis", True, "Process network cleared"]
        return ["stop vis", True, "No available network handler"]
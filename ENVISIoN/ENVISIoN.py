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

        if request[0] == "start vis":
            # request[1] is the visualization-type-string
            response = self.start_visualisation(request[1])
        elif request[0] == "stop vis":
            # request[1] is the visualization-type-string
            response = self.stop_visualization(request[1])
        elif request[0] == "edit":
            # request[1] is array containing 
            # visualization type, edit type, and edit data
            response = self.edit_visualization(request[1][0], request[1][1], request[1][2])
        
        return response
    
    def start_visualisation(self, vis_type):
    # Start visualizations here.
        if vis_type == "charge":
            try:
                self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", self.app)
                return ["start vis", True, ["charge", None]] # TODO return if unitcell was found
            except AssertionError as error:
                return ["start vis", False, ["charge", "Invalid HDF5 file."]]
        else:
            return ["start vis", False, [vis_type, "Unknown visualization type"]]

    def stop_visualization(self, vis_type):
        if vis_type == "all":
            self.app.network.clear()
            self.networkHandler = None
            return ["stop vis", True, ["all", "Processor network cleared"]]
        else:
            return ["stop vis", False, [vis_type, "Unknown visualization type"]]

    def edit_visualization(self, vis_type, edit_type, edit_data):
        if vis_type == "charge":
            if not type(self.networkHandler) is ChargeNetworkHandler:
                return ["edit", False, ["charge", "Visualization is not running"]]
            if edit_type == "add tf point":
                self.networkHandler.add_tf_point(edit_data[0], arr2col(edit_data))
                return ["edit", True, ["charge", "Color added."]]
            
    



def arr2col(arr):
    print("ARRAY HERE: ")
    print(arr)
    return ivw.glm.vec4(arr[0], arr[1], arr[2], arr[3])
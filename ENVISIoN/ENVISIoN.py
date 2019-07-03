#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

# TODO: Create some kind of dictionary that maps 
#       request strings onto functions.


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

        self.func_dict = {"start": lambda data: self.start_visualisation(data)}
        self.func_dict = {"stop": lambda data: self.stop_visualisation(data)}
        self.func_dict = {"edit": lambda data: self.edit_visualisation(data[0], data[1], data[2])}
        # self.func_dict = {"data request": lambda data: self.start_visualisation(data)}
        
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
    # Recieve a request, acts on it, then returns a response
    # See XXX.txt for request and response specifications.

        response = [request[0], False, "Unhandled request"]

        if request[0] == "start":
            # request[1] is the visualization-type-string
            response = self.start_visualisation(request[1])
        elif request[0] == "stop":
            # request[1] is the visualization-type-string
            response = self.stop_visualization(request[1])
        elif request[0] == "edit":
            # request[1] is array containing 
            # visualization type, edit type, and edit data
            response = self.edit_visualization(request[1][0], request[1][1], request[1][2])
        
        return response
    
    def start_visualisation(self, vis_type):
    # Start visualizations depending on vis_type.
        if vis_type == "charge":
            try:
                self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", self.app)
                return ["start", True, ["charge", None]] # TODO return if unitcell was found
            except AssertionError as error:
                return ["start", False, ["charge", "Invalid HDF5 file."]]
        else:
            return ["start", False, [vis_type, "Unknown visualization type"]]

    def stop_visualisation(self, vis_type):
    # Stop visualizations depending on vis_type.
        if vis_type == "all":
            self.app.network.clear()
            self.networkHandler = None
            return ["stop", True, ["all", "Processor network cleared"]]
        else:
            return ["stop", False, [vis_type, "Unknown visualization type"]]

    def edit_visualisation(self, vis_type, edit_type, edit_data):
    # Change some aspect of a running visualization.
        if vis_type == "charge":
            if not type(self.networkHandler) is ChargeNetworkHandler:
                return ["edit", False, ["charge", "Visualization is not running"]]
            if edit_type == "add tf point":
                self.networkHandler.add_tf_point(edit_data[0], arr2col(edit_data))
                return ["edit", True, ["charge", "Color added."]]
            
    



def arr2col(arr):
    return ivw.glm.vec4(arr[0], arr[1], arr[2], arr[3])
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
from processor_network.UnitcellNetworkHandler import UnitcellNetworkHandler
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
        self.networkHandlers = {}

        

        # Mapp action strings to functions
        self.action_dict = {}
        self.action_dict["start"] = lambda id, data: self.initialize_visualisation(id, data[0], data[1])
        self.action_dict["stop"] = lambda id, data: self.stop_visualisation(id, data)
        self.action_dict["add_tf_point"] = lambda id, data: self.networkHandlers[id].add_tf_point(data[0], arr2col(data[1]))
        self.action_dict["get_bands"] = lambda id, data: self.networkHandlers[id].get_available_bands(data)

        self.visualisationTypes = {
            "charge": ChargeNetworkHandler,
            "unitcell": UnitcellNetworkHandler}
        
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
    # Requests are on form [ACTION, ID, DATA]
        action, handler_id, data = request
        # Check if action exist
        if not action in self.action_dict:
            return [request[0], False, "Unknown action"]
        # Check if id exist
        if not handler_id in self.networkHandlers and (action != "start" and action != "stop"):
            return [action, False, "Non-existant network handler instance"]

        try:
        # Runs the funtion with networkhandler id and request data as arguments.
            return [action] + self.action_dict[action](handler_id, data)
        except AttributeError as error:
        # Triggered if network handler instance does not have desired function.
            return [request[0], False, "Action not found."]
    
    
    def initialize_visualisation(self, handler_id, vis_type, hdf5_file):
        # Initializes a network handler which will start a visualization.
        # Type of subclass depends on vis_type

        # TODO: add exception on file not found and faulty hdf5 file
        if handler_id in self.networkHandlers:
            return [False, handler_id + " visualisation is already running"]
        self.networkHandlers[handler_id] = self.visualisationTypes[vis_type](hdf5_file, self.app)
        return [True, vis_type + " visualisation started."]

    def stop_visualisation(self, handler_id, stop_all):
    # Stop visualizations depending on vis_type.
        if stop_all:
            self.app.network.clear()
            self.networkHandlers.clear()
            return [True, "All visualisations stopped."]
        elif handler_id in self.networkHandlers:
            self.networkHandlers[handler_id].clear_processor_network()
            del self.networkHandlers[handler_id]
            return [True, handler_id + " stopped."]
        else:
            return [False, "That visualisation is not running."]

def arr2col(arr):
    return ivw.glm.vec4(arr[0], arr[1], arr[2], arr[3])
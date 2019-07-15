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
from processor_network.ELFNetworkHandler import ELFNetworkHandler
from processor_network.UnitcellNetworkHandler import UnitcellNetworkHandler
from processor_network.BandstructureNetworkHandler import BandstructureNetworkHandler
from processor_network.PCFNetworkHandler import PCFNetworkHandler


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
        # Functions should always take one id and a list of parameters.
        self.action_dict = {}
        self.action_dict["start"] = lambda id, params: self.initialize_visualisation(id, *params)
        self.action_dict["stop"] = lambda id, params: self.stop_visualisation(id, *params)

        # Volume visualisation actions
        self.action_dict["set_mask"] = lambda id, params: self.networkHandlers[id].set_mask(*params)
        self.action_dict["clear_tf"] = lambda id, params: self.networkHandlers[id].clear_tf(*params)
        self.action_dict["set_tf_points"] = lambda id, params: self.networkHandlers[id].set_tf_points(*params)
        self.action_dict["add_tf_point"] = lambda id, params: self.networkHandlers[id].add_tf_point(*params)
        self.action_dict["remove_tf_point"] = lambda id, params: self.networkHandlers[id].remove_tf_point(*params)
        self.action_dict["set_tf_point_color"] = lambda id, params: self.networkHandlers[id].set_tf_point_color(*params)
        self.action_dict["get_tf_points"] = lambda id, params: self.networkHandlers[id].get_tf_points(*params)
        self.action_dict["set_shading_mode"] = lambda id, params: self.networkHandlers[id].set_shading_mode(*params)
        self.action_dict["set_volume_background"] = lambda id, params: self.networkHandlers[id].set_volume_background(*params)
        self.action_dict["set_slice_background"] = lambda id, params: self.networkHandlers[id].set_slice_background(*params)
        self.action_dict["toggle_slice_plane"] = lambda id, params: self.networkHandlers[id].toggle_slice_plane(*params)
        self.action_dict["set_plane_normal"] = lambda id, params: self.networkHandlers[id].set_plane_normal(*params)
        self.action_dict["set_plane_height"] = lambda id, params: self.networkHandlers[id].set_plane_height(*params)
        self.action_dict["position_canvases"] = lambda id, params: self.networkHandlers[id].position_canvases(*params)
        self.action_dict["toggle_slice_canvas"] = lambda id, params: self.networkHandlers[id].toggle_slice_canvas(*params)

        # Unicell visalisation actions
        self.action_dict["set_atom_radius"] = lambda id, params: self.networkHandlers[id].set_atom_radius(*params)
        self.action_dict["hide_atoms"] = lambda id, params: self.networkHandlers[id].hide_atoms(*params)
        self.action_dict["get_atom_name"] = lambda id, params: self.networkHandlers[id].get_atom_name(*params)
        self.action_dict["toggle_unitcell_canvas"] = lambda id, params: self.networkHandlers[id].toggle_unitcell_canvas(*params)
        self.action_dict["toggle_full_mesh"] = lambda id, params: self.networkHandlers[id].toggle_full_mesh(*params)
        self.action_dict["set_canvas_position"] = lambda id, params: self.networkHandlers[id].set_canvas_position(*params)

        # Charge and ELF visualisation actions
        self.action_dict["get_bands"] = lambda id, params: self.networkHandlers[id].get_available_bands(*params)
        self.action_dict["set_active_band"] = lambda id, params: self.networkHandlers[id].set_active_band(*params)

        self.visualisationTypes = {
            "charge": ChargeNetworkHandler,
            "unitcell": UnitcellNetworkHandler,
            "elf": ELFNetworkHandler,
            "pcf": PCFNetworkHandler,
            "bandstructure": BandstructureNetworkHandler}

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
        # Requests are on form [ACTION, HANDLER_ID, [PARAMETERS]]'
        action, handler_id, parameters = request


        # Check if action exist
        if not action in self.action_dict:
            return [request[0], False, "Unknown action"]
        # Check if id exist
        if not handler_id in self.networkHandlers and (action != "start" and action != "stop"):
            return [action, False, "Non-existant network handler instance"]

        # if action!="start":
        #     return [action, parameters]

        # try:
        # Runs the funtion with networkhandler id and request data as arguments.
        return [action] + self.action_dict[action](handler_id, parameters)
        # except AttributeError as error:
        # # Triggered if network handler instance does not have desired function.
        #     return [request[0], False, "Function does not exsist."]
        # except TypeError as error:
        #     return [request[0], False, "Bad parameters."]
    
    
    def initialize_visualisation(self, handler_id, vis_type, hdf5_file):
        # Initializes a network handler which will start a visualization.
        # Type of subclass depends on vis_type

        # TODO: add exception on file not found and faulty hdf5 file
        if handler_id in self.networkHandlers:
            return [False, handler_id + " visualisation is already running"]
        self.networkHandlers[handler_id] = self.visualisationTypes[vis_type](hdf5_file, self.app)
        return [True, [handler_id, vis_type]]

    def stop_visualisation(self, handler_id, stop_all=False):
    # Stop visualizations depending on vis_type.
        if stop_all:
            ids = tuple(self.networkHandlers)
            for id in ids:
                self.networkHandlers[id].clear_processors()
            self.app.network.clear()
            self.networkHandlers.clear()
            return [True, ids]
        if handler_id in self.networkHandlers:
            self.networkHandlers[handler_id].clear_processors()
            del self.networkHandlers[handler_id]
            return [True, handler_id]
        # elif handler_id in self.networkHandlers:
        #     self.networkHandlers[handler_id].clear_processor_network()
        #     del self.networkHandlers[handler_id]
        #     return [True, handler_id + " stopped."]
        # else:
        return [False, "That visualisation is not running."]


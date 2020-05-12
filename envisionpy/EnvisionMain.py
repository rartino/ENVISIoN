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

import sys,os, time


if 'INVIWO_HOME' in os.environ and os.environ['INVIWO_HOME'] not in sys.path:
    sys.path.append(os.environ['INVIWO_HOME'])

try:
    import inviwopy as ivw
    import inviwopyapp as ivwapp
except ModuleNotFoundError as e:
    sys.stderr.write("Module error: " + str(e) + "\n" + "Can not find module. Please check that the environment variable INVIWO_HOME is set to the correct value in the computers system settings.")
    #raise Exception("Can not find module. Please set the environment variable INVIWO_HOME to the correct value.")

"""
if 'INVIWO_HOME' in os.environ and os.environ['INVIWO_HOME'] not in sys.path:
    sys.path.insert(0,os.environ['INVIWO_HOME'])
        
try:
    import inviwopy as ivw
    import inviwopyapp as ivwapp
except ModuleNotFoundError as e:
    path_canidates = [os.path.realpath(os.path.join(__file__,"..","..","..","inviwo-build","bin")), "/opt/envision/inviwo/bin" ]
    for path_candidate in path_canidates:
        if os.path.exists(path_candidate):
            sys.path.append(path_candidate)        
            import inviwopy as ivw
            import inviwopyapp as ivwapp
            break
    else:
        raise Exception("Cannot find inviwo directory. Please set environment variable INVIWO_HOME to point at the directory to use.")
     """   
from envisionpy.processor_network import *
from envisionpy.utils.exceptions import *
import envisionpy.hdf5parser


class EnvisionMain():
    """ Class for managing a inviwo instance 
        and running ENVISIoN visualizations with it.

        Acts as an interface to control all aspects of envision.

        Can be used by different interfaces as long as they send requests using
        the same JSON standard.
    """
    def __init__(self):
        self.app = None
        self.initialize_inviwo_app()
        self.networkHandlers = {}

        # Mapp action strings to functions
        # Functions should always take one id and a list of parameters.
        self.action_dict = {}
        self.action_dict["start"] = lambda id, params: self.initialize_visualisation(id, *params)
        self.action_dict["stop"] = lambda id, params: self.stop_visualisation(id, *params)
        self.action_dict["get_ui_data"] = lambda id, params: self.networkHandlers[id].get_ui_data(*params)
        self.action_dict["position_canvases"] = lambda id, params: self.networkHandlers[id].position_canvases(*params)

        # Volume visualisation actions
        self.action_dict["clear_tf"] = lambda id, params: self.networkHandlers[id].clear_tf(*params)
        self.action_dict["set_tf_points"] = lambda id, params: self.networkHandlers[id].set_tf_points(*params)
        self.action_dict["add_tf_point"] = lambda id, params: self.networkHandlers[id].add_tf_point(*params)
        # self.action_dict["remove_tf_point"] = lambda id, params: self.networkHandlers[id].remove_tf_point(*params)
        self.action_dict["get_tf_points"] = lambda id, params: self.networkHandlers[id].get_tf_points(*params)
        self.action_dict["set_shading_mode"] = lambda id, params: self.networkHandlers[id].set_shading_mode(*params)
        self.action_dict["set_volume_background"] = lambda id, params: self.networkHandlers[id].set_volume_background(*params)
        self.action_dict["set_slice_background"] = lambda id, params: self.networkHandlers[id].set_slice_background(*params)
        self.action_dict["toggle_slice_plane"] = lambda id, params: self.networkHandlers[id].toggle_slice_plane(*params)
        self.action_dict["set_plane_normal"] = lambda id, params: self.networkHandlers[id].set_plane_normal(*params)
        self.action_dict["set_plane_height"] = lambda id, params: self.networkHandlers[id].set_plane_height(*params)
        self.action_dict["toggle_slice_canvas"] = lambda id, params: self.networkHandlers[id].toggle_slice_canvas(*params)
        self.action_dict["set_texture_wrap_mode"] = lambda id, params: self.networkHandlers[id].set_texture_wrap_mode(*params)
        self.action_dict["set_slice_zoom"] = lambda id, params: self.networkHandlers[id].set_slice_zoom(*params)
        self.action_dict["show_volume_dist"] = lambda id, params: self.networkHandlers[id].show_volume_dist(*params)
        self.action_dict["toggle_transperancy_before"] = lambda id, params: self.networkHandlers[id].toggle_transperancy_before(*params)
        # self.action_dict["toggle_tf_editor"] = lambda id, params: self.networkHandlers[id].toggle_tf_editor(*params)

        # Unitcell visalisation actions
        self.action_dict["set_atom_radius"] = lambda id, params: self.networkHandlers[id].set_atom_radius(*params)
        self.action_dict["hide_atoms"] = lambda id, params: self.networkHandlers[id].hide_atoms(*params)
        self.action_dict["get_atom_name"] = lambda id, params: self.networkHandlers[id].get_atom_name(*params)
        self.action_dict["get_atom_names"] = lambda id, params: self.networkHandlers[id].get_atom_names(*params)
        self.action_dict["toggle_unitcell_canvas"] = lambda id, params: self.networkHandlers[id].toggle_unitcell_canvas(*params)
        self.action_dict["toggle_full_mesh"] = lambda id, params: self.networkHandlers[id].toggle_full_mesh(*params)
        self.action_dict["set_canvas_position"] = lambda id, params: self.networkHandlers[id].set_canvas_position(*params)

        # Charge and ELF visualisation actions
        self.action_dict["get_bands"] = lambda id, params: self.networkHandlers[id].get_available_bands(*params)
        self.action_dict["set_active_band"] = lambda id, params: self.networkHandlers[id].set_active_band(*params)

        # Parchg visualisation actions
        self.action_dict["select_bands"] = lambda id, params: self.networkHandlers[id].select_bands(*params)

        # Line plot
        self.action_dict["set_x_range"] = lambda id, params: self.networkHandlers[id].set_x_range(*params)
        self.action_dict["set_y_range"] = lambda id, params: self.networkHandlers[id].set_y_range(*params)
        self.action_dict["toggle_vertical_line"] = lambda id, params: self.networkHandlers[id].toggle_vertical_line(*params)
        self.action_dict["set_vertical_line_x"] = lambda id, params: self.networkHandlers[id].set_vertical_line_x(*params)
        self.action_dict["toggle_grid"] = lambda id, params: self.networkHandlers[id].toggle_grid(*params)
        self.action_dict["set_grid_size"] = lambda id, params: self.networkHandlers[id].set_grid_size(*params)
        self.action_dict["toggle_x_label"] = lambda id, params: self.networkHandlers[id].toggle_x_label(*params)
        self.action_dict["toggle_y_label"] = lambda id, params: self.networkHandlers[id].toggle_y_label(*params)
        self.action_dict["set_n_labels"] = lambda id, params: self.networkHandlers[id].set_n_labels(*params)
        self.action_dict["set_y_selection_type"] = lambda id, params: self.networkHandlers[id].set_y_selection_type(*params)
        self.action_dict["get_available_datasets"] = lambda id, params: self.networkHandlers[id].get_available_datasets(*params)
        self.action_dict["set_y_single_selection_index"] = lambda id, params: self.networkHandlers[id].set_y_single_selection_index(*params)
        self.action_dict["set_y_multi_selection"] = lambda id, params: self.networkHandlers[id].set_y_multi_selection(*params)
        # self.action_dict["set_y_single_selection"] = lambda id, params: self.networkHandlers[id].set_y_single_selection(*params)
        # self.action_dict["set_y_single_selection"] = lambda id, params: self.networkHandlers[id].set_y_single_selection(*params)

        # DoS
        self.action_dict["toggle_total"] = lambda id, params: self.networkHandlers[id].toggle_total(*params)
        self.action_dict["toggle_partial"] = lambda id, params: self.networkHandlers[id].toggle_partial(*params)
        self.action_dict["set_partial_selection"] = lambda id, params: self.networkHandlers[id].set_partial_selection(*params)



        self.visualisationTypes = {
            "charge": ChargeNetworkHandler,
            "elf": ELFNetworkHandler,
            "parchg": ParchgNetworkHandler,
            "unitcell": UnitcellNetworkHandler,
            "pcf": PCFNetworkHandler,
            "bandstructure": BandstructureNetworkHandler,
            "dos": DOSNetworkHandler,
            "bandstructure3d": Bandstructure3DNetworkHandler
            }

        # print(dir(hdf5parser.vasp))
        self.parseFunctions = {
            "charge": envisionpy.hdf5parser.charge,
            "Electron density": envisionpy.hdf5parser.charge,
            "elf": envisionpy.hdf5parser.elf, 
            "Electron localisation function": envisionpy.hdf5parser.elf,
            "Partial charge density": envisionpy.hdf5parser.parchg,
            "parchg": envisionpy.hdf5parser.parchg,
            "unitcell": envisionpy.hdf5parser.unitcell,
            "Unitcell": envisionpy.hdf5parser.unitcell,
            "bandstructure": envisionpy.hdf5parser.bandstructure,
            "Bandstructure": envisionpy.hdf5parser.bandstructure,
            "pcf": envisionpy.hdf5parser.paircorrelation,
            "Pair correlation function": envisionpy.hdf5parser.paircorrelation,
            "dos": envisionpy.hdf5parser.dos,
            "Density of states": envisionpy.hdf5parser.dos
        }

    def update(self):
        self.app.update()

    def initialize_inviwo_app(self):
        # Inviwo requires that a logcentral is created.
        self.lc = ivw.LogCentral()
        
        # Create and register a console logger
        self.cl = ivw.ConsoleLogger()
        self.lc.registerLogger(self.cl)

        # Create the inviwo application
        self.app = ivwapp.InviwoApplicationQt()
        self.app.registerModules()

        # load a workspace
        # self.app.network.load(self.app.getPath(ivw.PathType.Workspaces) + "/boron.inv")

        # Make sure the app is ready
        self.app.update()
        self.app.waitForPool()
        self.app.update()
        self.app.network.clear()

    def handle_vis_request(self, request):
        # Recieve a request, acts on it, then returns a response
        # Requests are on form [ACTION, HANDLER_ID, [PARAMETERS]]'
        action, handler_id, parameters = request


        # Check if action exist
        if not action in self.action_dict:
            return [request[0], False, handler_id, format_error(InvalidRequestError("Unknown action"))]
        # Check if id exist
        if not handler_id in self.networkHandlers and (action != "start" and action != "stop"):
            return [action, False, handler_id, format_error(HandlerNotFoundError('Non-existant network handler instance "' + handler_id + '".'))]

        # if action!="start":
        #     return [action, parameters]

        # try:
        # Runs the funtion with networkhandler id and request data as arguments.
        try:
            response_data = self.action_dict[action](handler_id, parameters)
        except HandlerNotFoundError as e:
            return [action, False, handler_id, format_error(e)]
        except BadHDF5Error as e:
            return [action, False, handler_id, format_error(e)]
        except HandlerAlreadyExistError as e:
            return [action, False, handler_id, format_error(e)]
        # except EnvisionError as e:
        #     return [action, False, handler_id, format_error(e)]
        else:
            return [action, True, handler_id, response_data] #returns -> "response" in nodeInterface.py

        # return [action] + self.action_dict[action](handler_id, parameters)
        # except AttributeError as error:
        # # Triggered if network handler instance does not have desired function.
        #     return [request[0], False, "Function does not exsist."]
        # except TypeError as error:
        #     return [request[0], False, "Bad parameters."]


    def handle_parse_request(self, request):
        # Requests are on form [[PARSE_TYPES...], HDF5_PATH, VASP_PATH]
        parse_types, hdf5_path, vasp_path = request

        if parse_types == "All":
            parse_types = [
                "Electron density", 
                "Electron localisation function",
                "Partial charge density",
                "Unitcell",
                "Bandstructure", 
                "Pair correlation function",
                "Density of states"]

        parse_statuses = {}
        for parse_type in parse_types:
            parse_statuses[parse_type] = self.parseFunctions[parse_type](hdf5_path, vasp_path)

        # TODO: Return status of 
        return [parse_statuses, "*Error message*"]


    def initialize_visualisation(self, handler_id, vis_type, hdf5_file, name=None, datasetName=None):
        # Initializes a network handler which will start a visualization.
        # Type of subclass depends on vis_type

        # TODO: add exception on file not found and faulty hdf5 file
        if handler_id in self.networkHandlers:
            raise HandlerAlreadyExistError("Already starting that visualisation " + handler_id + ". Wait a bit and try again.")
        self.networkHandlers[handler_id] = self.visualisationTypes[vis_type](hdf5_file, self.app)

        return [handler_id, vis_type, name, datasetName]

    def stop_visualisation(self, handler_id, stop_all=False):
    # Stop visualizations depending on vis_type.
        if stop_all:
            ids = tuple(self.networkHandlers)
            for id in ids:
                self.networkHandlers[id].clear_processors()
            self.app.network.clear()
            self.networkHandlers.clear()
            return ids
        if handler_id in self.networkHandlers:
            self.networkHandlers[handler_id].clear_processors()
            del self.networkHandlers[handler_id]
            return handler_id
        # elif handler_id in self.networkHandlers:
        #     self.networkHandlers[handler_id].clear_processor_network()
        #     del self.networkHandlers[handler_id]
        #     return [True, handler_id + " stopped."]
        # else:
        raise HandlerNotFoundError("That visualisation is not running.")


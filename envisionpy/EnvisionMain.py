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

import sys, os, time


if 'INVIWO_HOME' in os.environ and os.environ['INVIWO_HOME'] not in sys.path:
    sys.path.append(os.environ['INVIWO_HOME'])

# sys.path.append("C:/Kandidatprojekt/inviwo-build/bin/Release")

try:
    import inviwopy as ivw
    import inviwopyapp as ivwapp
except ModuleNotFoundError as e:
    sys.stderr.write("Module error: " + str(e) + "\n" + "Can not find module. Please check that the environment variable INVIWO_HOME is set to the correct value in the computers system settings.")
    #raise Exception("Can not find module. Please set the environment variable INVIWO_HOME to the correct value.")

from envisionpy.network import VisualisationManager
from envisionpy.utils.exceptions import *
import envisionpy.hdf5parser


class EnvisionMain():
    """ Class for managing a inviwo instance
        and running ENVISIoN visualizations with it.

        Can be used by different interfaces as long as they send requests using
        the same JSON standard.
    """
    def __init__(self):
        self.app = None
        self.initialize_inviwo_app()

        self.visualisation_managers = {}

        # self.ui_callable = [
        # ]

        # Map request strings to parse functions.
        self.parse_functions = {
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
            "Density of states": envisionpy.hdf5parser.dos,
            "fermisurface": envisionpy.hdf5parser.fermi_parser,
            "Fermi surface": envisionpy.hdf5parser.fermi_parser,
            "Force": envisionpy.hdf5parser.force_parser,
            "Molecular dynamics": envisionpy.hdf5parser.mol_dynamic_parser
        }
        self.parse_functions_ELK = {
            "Unitcell": envisionpy.hdf5parser.unitcell_parser
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

        print(dir(self.app))

    def handle_request(self, request):
        # Request should be a dictionary with a string specifying a function in 'type'
        # and a list of function arguments in 'parameters'
        print(request)

        # TODO: Allow only a subset of functions to pass.
        if request['type'] not in dir(self):
            response_data = 'Unhandled request'

        # Run function based on request type.
        func = getattr(self, request['type'])
        response_data = func(*request['parameters'])

        response_packet = {
            'type': request['type'],
            'data': response_data}
        return response_packet

# Functions callable from UI

    def parse_vasp(self, vasp_path, hdf5_path, parse_types):
        if parse_types != 'All' and not all(elem in self.parse_functions for elem in parse_types):
            raise EnvisionError('Invalid parse type.')


        if parse_types == "All":
            parse_types = [
                "Electron density",
                "Electron localisation function",
                "Partial charge density",
                "Unitcell",
                "Bandstructure",
                "Pair correlation function",
                "Density of states",
                "Fermi surface",
                "Force",
                "Molecular dynamics"]

        parse_statuses = {}
        for parse_type in parse_types:
            try:
                parse_statuses[parse_type] = self.parse_functions[parse_type](hdf5_path, vasp_path)
            except Exception:
                parse_statuses[parse_type] = False
                print("Parser {} could not be parsed some functions may not work.".format(parse_type))

        return [parse_statuses]

    def parse_ELK(self, ELK_path, hdf5_path, parse_types):
        if parse_types != 'All' and not all(elem in self.parse_functions_ELK for elem in parse_types):
            raise EnvisionError('Invalid parse type.')


        if parse_types == "All":
            parse_types = ["Unitcell"]

        parse_statuses = {}
        for parse_type in parse_types:
            try:
                parse_statuses[parse_type] = self.parse_functions_ELK[parse_type](hdf5_path, ELK_path)
            except Exception:
                parse_statuses[parse_type] = False
                print("Parser {} could not be parsed some functions may not work.".format(parse_type))

        return [parse_statuses]

    def init_manager(self, hdf5_path, identifier=None):
        if identifier == None:
            identifier = os.path.splitext(hdf5_path)[0].split('/')[-1]
        base_id = identifier
        # Make sure identifier is unique
        n = 1
        while identifier in self.visualisation_managers:
            identifier = base_id + str(n)
            n += 1
        visualisationManager = VisualisationManager(hdf5_path, self.app)
        self.visualisation_managers[identifier] = visualisationManager
        return [identifier, hdf5_path, visualisationManager.available_visualisations]

    def close_manager(self, identifier):
        if identifier not in self.visualisation_managers:
            raise EnvisionError('Tried to close non existant visualisation manager id:'+identifier+".")
        self.visualisation_managers[identifier].stop()
        del self.visualisation_managers[identifier]
        return identifier

    def start_visualisation(self, identifier, vis_type, bool = True):
        if identifier not in self.visualisation_managers:
            raise EnvisionError('No visualisation manager with id:'+identifier+" has been initialized.")
        self.visualisation_managers[identifier].start(vis_type, bool)
        return [identifier, vis_type]

    def stop_visualisation(self, identifier, vis_type):
        if identifier not in self.visualisation_managers:
            return False
        self.visualisation_managers[identifier].stop(vis_type)
        return [identifier, vis_type]

    def visualisation_request(self, identifier, vis_type, function_name, param_list=[]):
        print(param_list)
        if identifier not in self.visualisation_managers:
            return False
        return self.visualisation_managers[identifier].call_subnetwork(vis_type, function_name, param_list)

    def reset_canvas_positions(self, start_x ,start_y):
        for manager in self.visualisation_managers.values():
            manager.reset_canvas_positions(start_x, start_y)
            start_y += 500



    def get_ui_data(self, identifier):
        if identifier not in self.visualisation_managers:
            return False
        return self.visualisation_managers[identifier].get_ui_data()

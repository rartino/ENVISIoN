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
        # self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", self.app)
        # self.networkHandler = None
        # Inviwo requires that a logcentral is created.
        

        
    def update(self):
        self.app.update()

    def initialize_inviwo_app(self):
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
        # self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", app)
        
        # return app

    def handle_request(self, request):
        # TODO lotsa try catch
        response = ["nothing done"]

        if request["data"] == "start charge":
            try:
                self.networkHandler = ChargeNetworkHandler("/home/labb/HDF5/nacl_new.hdf5", self.app)
                response = ["success", "charge started"]
            except AssertionError as error:
                response = ["failure", "charge not started"]
        # elif request["data"] == "end charge":
        #     self.networkHandler.clear_processor_network()
        #     del self.networkHandler
        #     response = "Response", "charge stopped"
        
        return response
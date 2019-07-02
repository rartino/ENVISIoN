#
#  Created by Jesper Ericsson
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys,os,inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append("/home/labb/Inviwo-latest/build/bin")
import inviwopy as ivw
import inviwopyapp as qt
import time

class ENVISIoN():
    """ Class for managing a inviwo instance 
        and running ENVISIoN visualizations with it.

        Acts as an interface to control all aspects of envision.

    """
    def __init__(self):
        self.app = self.initialize_inviwo_app()

    def update(self):
        self.app.update()

    def initialize_inviwo_app(self):

        # Inviwo requires that a logcentral is created.
        lc = ivw.LogCentral()
        
        # Create and register a console logger
        cl = ivw.ConsoleLogger()
        lc.registerLogger(cl)

        # Create the inviwo application
        app = qt.InviwoApplicationQt()
        app.registerModules()

        # load a workspace
        app.network.load(app.getPath(ivw.PathType.Workspaces) + "/boron.inv")

        # Make sure the app is ready
        app.update()
        app.waitForPool()
        app.update()
        return app
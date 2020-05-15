#  ENVISIoN
#
#  Copyright (c) 2020 Alexander Vevstad
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
import inviwopy.glm as glm

from .NetworkHandler import NetworkHandler


class FermiSurfaceNetworkHandler(NetworkHandler):
    def __init__(self, hdf_file_path, inviwoApp):
        self.app = inviwoApp
        self.setup_network()
        self.filepath = hdf_file_path

    def setup_network(self):
        app = self.app
        network = app.network
        factory = app.processorFactory
        app.registerModules()

        # start with a clean network
        network.clear()

        hdf_fermi_source = factory.create('org.inviwo.HDF5FermiSource', glm.ivec2(0,0))
        hdf_fermi_source.filename.value = self.filepath
        network.addProcessor(hdf_fermi_source)

        cube_proxy_geometry = factory.create('org.inviwo.CubeProxyGeometry', glm.ivec2(50,100))
        network.addProcessor(cube_proxy_geometry)

        network.addConnection(
            hdf_fermi_source.getOutport('outport'),
            cube_proxy_geometry.getInport('volume')
        )

        volume_bounding_box = factory.create('org.inviwo.VolumeBoundingBox', glm.ivec2(250,100))
        network.addProcessor(volume_bounding_box)

        network.addConnection(
            hdf_fermi_source.getOutport('outport'),
            volume_bounding_box.getInport('volume')
        )

        background = factory.create('org.inviwo.Background', glm.ivec2(450, 100))
        network.addProcessor(background)

        entry_exit_points = factory.create('org.inviwo.EntryExitPoints', glm.ivec2(50, 200))
        network.addProcessor(entry_exit_points)

        network.addConnection(
            cube_proxy_geometry.getOutport('proxyGeometry'),
            entry_exit_points.getInport('geometry')
        )

        mesh_renderer = factory.create('org.inviwo.GeometryRenderGL', glm.ivec2(250, 200))
        network.addProcessor(mesh_renderer)

        network.addConnection(
            volume_bounding_box.getOutport('mesh'),
            mesh_renderer.getInport('geometry')
        )

        network.addConnection(
            background.getOutport('outport'),
            mesh_renderer.getInport('imageInport')
        )


        network.addLink(
            mesh_renderer.getPropertyByIdentifier('camera'),
            entry_exit_points.getPropertyByIdentifier('camera')
        )

        iso_raycaster = factory.create('org.inviwo.ISORaycaster', glm.ivec2(0, 300))
        network.addProcessor(iso_raycaster)

        network.addConnection(
            hdf_fermi_source.getOutport('outport'),
            iso_raycaster.getInport('volume')
        )

        network.addConnection(
            entry_exit_points.getOutport('entry'),
            iso_raycaster.getInport('entry')
        )

        network.addConnection(
            entry_exit_points.getOutport('exit'),
            iso_raycaster.getInport('exit')
        )

        network.addConnection(
            mesh_renderer.getOutport('image'),
            iso_raycaster.getInport('bg')
        )

        canvas = factory.create('org.inviwo.CanvasGL', glm.ivec2(0, 400))
        network.addProcessor(canvas)

        network.addConnection(
            iso_raycaster.getOutport('outport'),
            canvas.getInport('inport')
        )

        network.addLink(
            entry_exit_points.getPropertyByIdentifier('camera'),
            iso_raycaster.getPropertyByIdentifier('camera')
        )

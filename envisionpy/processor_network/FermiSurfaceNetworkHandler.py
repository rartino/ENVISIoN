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
import h5py

from .NetworkHandler import NetworkHandler
from inviwo.modules.fermi.processors.HDF5FermiSource import HDF5FermiSource


class FermiSurfaceNetworkHandler(NetworkHandler):
    def __init__(self, hdf_file_path, inviwoApp):
        super().__init__(inviwoApp)
        self.setup_network(hdf_file_path)

    def get_ui_data(self):
        return [
        "fermisurface",
        [
        self.get_available_bands(),
        self.get_active_band()
        ],
        self.get_active_fermi_level()
        ]
    
    def get_active_band(self):
        source = self.hdf_fermi_source
        band_index = str(source.energy_band.value)
        index = self.get_available_bands().index(band_index)
        return index

    def get_available_bands(self):
        source = self.hdf_fermi_source
        path = source.filename.value
        with h5py.File(path, 'r') as f:
            band_keys = []
            for key in f.get('bands').keys():
                band_keys.append(key)
            return band_keys

    def get_active_fermi_level(self):
        active_fermi_level = self.iso_raycaster.raycasting.isoValue.value
        return active_fermi_level

# ------------------------------------------
# ------- Property control functions -------
    
    def set_active_band(self, key):
    # Sets the dataset (band) which HDF5 Fermi Source processor will read
        source = self.hdf_fermi_source
        source.energy_band.value = int(key)
        
    def toggle_brillouin_zone(self, enable):
        source = self.hdf_fermi_source
        source.is_brillouin_zone.value = not source.is_brillouin_zone.value

    def toggle_expanded_zone(self, enable):
        source = self.hdf_fermi_source
        source.is_expanded_zone.value = not source.is_expanded_zone.value

    def set_fermi_level(self, value):
        self.iso_raycaster.raycasting.isoValue.value = float(value)

# ------------------------------------------
# ------- Network building functions -------

    def setup_network(self, filepath):
        app = self.app
        network = app.network
        factory = app.processorFactory

        # start with a clean network
        network.clear()

        #hdf_fermi_source = factory.create('org.inviwo.HDF5FermiSource', glm.ivec2(0,0))
        self.hdf_fermi_source = HDF5FermiSource('fermi', 'fermi source')
        self.hdf_fermi_source.filename.value = filepath
        network.addProcessor(self.hdf_fermi_source)

        cube_proxy_geometry = factory.create('org.inviwo.CubeProxyGeometry', glm.ivec2(50,100))
        network.addProcessor(cube_proxy_geometry)

        network.addConnection(
            self.hdf_fermi_source.getOutport('outport'),
            cube_proxy_geometry.getInport('volume')
        )

        volume_bounding_box = factory.create('org.inviwo.VolumeBoundingBox', glm.ivec2(250,100))
        network.addProcessor(volume_bounding_box)

        network.addConnection(
            self.hdf_fermi_source.getOutport('outport'),
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

        self.iso_raycaster = factory.create('org.inviwo.ISORaycaster', glm.ivec2(0, 300))
        network.addProcessor(self.iso_raycaster)

        network.addConnection(
            self.hdf_fermi_source.getOutport('outport'),
            self.iso_raycaster.getInport('volume')
        )

        network.addConnection(
            entry_exit_points.getOutport('entry'),
            self.iso_raycaster.getInport('entry')
        )

        network.addConnection(
            entry_exit_points.getOutport('exit'),
            self.iso_raycaster.getInport('exit')
        )

        network.addConnection(
            mesh_renderer.getOutport('image'),
            self.iso_raycaster.getInport('bg')
        )

        canvas = factory.create('org.inviwo.CanvasGL', glm.ivec2(0, 400))
        network.addProcessor(canvas)

        network.addConnection(
            self.iso_raycaster.getOutport('outport'),
            canvas.getInport('inport')
        )

        network.addLink(
            entry_exit_points.getPropertyByIdentifier('camera'),
            self.iso_raycaster.getPropertyByIdentifier('camera')
        )
        
        canvas.inputSize.dimensions.value = glm.size2_t(500,500)
        canvas.widget.show()

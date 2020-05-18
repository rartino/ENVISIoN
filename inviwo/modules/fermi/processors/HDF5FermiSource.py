# Name: HDF5FermiSource
from pathlib import Path

import inviwopy as ivw
import h5py
import numpy as np


class HDF5FermiSource(ivw.Processor):
    def __init__(self, id, name):
        ivw.Processor.__init__(self, id, name)

        self.volumeOutport = ivw.data.VolumeOutport('outport')
        self.addOutport(self.volumeOutport, owner=False)

        self.filename = ivw.properties.FileProperty("file", "HDF5 (.hdf)")
        self.addProperty(self.filename, owner=False)

        self.energy_band = ivw.properties.IntProperty('energy_band', 'Energy band')
        self.addProperty(self.energy_band, owner=False)

        self.is_brillouin_zone = ivw.properties.BoolProperty('brillouin_zone', 'Brillouin Zone')
        self.addProperty(self.is_brillouin_zone, owner=False)

        self.is_expanded_zone = ivw.properties.BoolProperty('expanded_zone', 'Expanded Zone')
        self.addProperty(self.is_expanded_zone, owner=False)

    @staticmethod
    def processorInfo():
        return ivw.ProcessorInfo(
            classIdentifier = "org.inviwo.HDF5FermiSource",
            displayName = "Fermi Source",
            category = "Python",
            codeState = ivw.CodeState.Stable,
            tags = ivw.Tags.PY
        )

    def getProcessorInfo(self):
        return HDF5FermiSource.processorInfo()

    def initializeResources(self):
        pass

    def brillouin_zone(self, matrix, basis):

        base_x = basis[0]
        base_y = basis[1]
        base_z = basis[2]
        matrix = self.expand(matrix)

        for x in range(matrix.shape[0]):
            for y in range(matrix.shape[1]):
                for z in range(matrix.shape[2]):
                    if np.dot(base_x, np.array([x-base_x[0],y-base_x[1],z-base_x[2]])) < 0:
                        matrix[x,y,z] = None

                    if np.dot(base_y, np.array([x-base_y[0],y-base_y[1],z-base_y[2]])) < 0:
                        matrix[x,y,z] = None

                    if np.dot(base_z, np.array([x-base_z[0],y-base_z[1],z-base_z[2]])) < 0:
                        matrix[x,y,z] = None

                    if np.dot(base_x, np.array([x-50*base_x[0],y-50*base_x[1],z-50*base_x[2]])) > 0:
                        matrix[x,y,z] = None

                    if np.dot(base_y, np.array([x-50*base_y[0],y-50*base_y[1],z-50*base_y[2]])) > 0:
                        matrix[x,y,z] = None

                    if np.dot(base_z, np.array([x-50*base_z[0],y-50*base_z[1],z-50*base_z[2]])) > 0:
                        matrix[x,y,z] = None

        return matrix

    def expand(self, matrix):
        lenx = matrix.shape[0]
        leny = matrix.shape[1]
        lenz = matrix.shape[2]

        new = np.zeros((2*lenx, 2*leny, 2*lenz), dtype=np.float32)
        new[0:lenx, 0:leny, 0:lenz] = matrix
        new[lenx:2*lenx, 0:leny, 0:lenz] = matrix

        new[0:lenx, leny:2*leny, 0:lenz] = matrix
        new[lenx:2*lenx, leny:2*leny, 0:lenz] = matrix

        new[0:lenx, 0:leny, lenz:2*lenz] = matrix
        new[lenx:2*lenx, 0:leny, lenz:2*lenz] = matrix

        new[0:lenx, leny:2*leny, lenz:2*lenz] = matrix
        new[lenx:2*lenx, leny:2*leny, lenz:2*lenz] = matrix

        return new

    def process(self):
        if len(self.filename.value) == 0 or not Path(self.filename.value).exists():
            return

        band_index = self.energy_band.value
        with h5py.File(self.filename.value, 'r') as f:
            basis = f.get('basis').value
            fermi_energy = f.get('fermi_energy')[()]

            matrix = f.get('bands').get(str(band_index)).get('composition')[()]

            self.energy_band.minValue = 0
            self.energy_band.maxValue = len(f.get('bands')) - 1


        # normalize all data points
        emax = matrix.max()
        emin = matrix.min()

        def normalize(value):
            return (value - emin) / (emax - emin)

        normalize_vector = np.vectorize(normalize)
        matrix = normalize_vector(matrix)

        if self.is_brillouin_zone.value:
            matrix = self.brillouin_zone(matrix, basis)
        elif self.is_expanded_zone.value:
            matrix = self.expand(matrix)

        volumes = ivw.data.Volume(matrix)
        volumes.dataMap.dataRange = ivw.glm.dvec2(0, 1)
        volumes.dataMap.valueRange = ivw.glm.dvec2(0, 1)


        # expand basis vector into a 4x4 matrix
        matrix = np.identity(4)
        matrix[:3, :-1] = basis
        volumes.modelMatrix = ivw.glm.mat4(*matrix.flatten())

        print('E-Fermi: {}'.format(fermi_energy))
        print('E-Fermi Normal: {}'.format(normalize(fermi_energy)))
        print('E-Min: {}'.format(emax))
        print('E-Max: {}'.format(emin))

        self.volumeOutport.setData(volumes)

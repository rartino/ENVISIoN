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
        self.addProperty(self.energy_band)

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

    def brillouin_zone(self, matrix):
        print(matrix.shape[0]/2)

        matrix = matrix[0:int(matrix.shape[0]/2),
                        0:int(matrix.shape[1]/2),
                        0:int(matrix.shape[2]/2)]


        return matrix

    def process(self):
        if len(self.filename.value) == 0 or not Path(self.filename.value).exists():
            return

        band_index = self.energy_band.value
        with h5py.File(self.filename.value, 'r') as f:
            basis = f.get('basis')[()]
            fermi_energy = f.get('fermi_energy')[()]

            evalues = f.get('bands').get(str(band_index)).get('composition')[()]

            self.energy_band.minValue = 0
            self.energy_band.maxValue = len(f.get('bands')) - 1


        # normalize all data points
        emax = evalues.max()
        emin = evalues.min()

        def normalize(value):
            return (value - emin) / (emax - emin)

        normalize_vector = np.vectorize(normalize)
        normalize_evalues = normalize_vector(evalues)
        print(normalize_evalues.shape)

        volumes = ivw.data.Volume(normalize_evalues)
        volumes.dataMap.dataRange = ivw.glm.dvec2(0, 1)
        volumes.dataMap.valueRange = ivw.glm.dvec2(0, 1)

        # expand basis vector into a 4x4 matrix
        matrix = np.identity(4)
        matrix[:3, :-1] = basis
        volumes.worldMatrix = ivw.glm.mat4(*matrix.flatten())

        print('E-Fermi: {}'.format(fermi_energy))
        print('E-Fermi Normal: {}'.format(normalize(fermi_energy)))
        print('E-Min: {}'.format(emax))
        print('E-Max: {}'.format(emin))

        self.volumeOutport.setData(volumes)

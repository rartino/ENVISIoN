#
#  ENVISIoN
#
#  Copyright (c) 2017-2019 Alexander Vevstad
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
from pathlib import Path

import inviwopy as ivw
import h5py
import numpy as np


class HDF5FermiSource(ivw.Processor):
    '''
    Process used for reading HDF5 data pertaining to fermi surface data

    Outport
    -------

    volumeOutport: ivw.data.VolumeOutport
        Final processed data

    Properties
    ----------

    energy_band: ivw.properties.IntProperty
        Specifiees the band that should be read from the HDF5 file

    is_brillouin_zone: ivw.propertiesBoolProperty
        Specifies if the data should be translated to birllouin zone

    is_expanded_zone: ivw.propertiesBoolProperty
        Specifies if the data should be translated to expanded zone.
        Note if is_brillouin_zone is set this property will be overriden
    '''
    def __init__(self, id, name):
        '''
        Parameters
        ----------

        id: str
            id given to the process

        name: str
            name given to the process
        '''
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

        self.fermi_level = ivw.properties.FloatProperty('fermi_level', 'Fermi Level')
        self.fermi_level.minValue = 0
        self.fermi_level.maxValue = 1
        self.addProperty(self.fermi_level, owner=False)

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
        '''
        Transforms reciprocal lattice to brillouin zone

        Parameters
        ------

        matrix: numpy.array
            3D Matrix should represent reciprocal lattice

        basis:
            Reciprocal basis vectors

        Return
        ------

            Matrix representing the brillouin zone
        '''
        base_x = basis[0]
        base_y = basis[1]
        base_z = basis[2]

        base_xy = base_x - base_y
        base_xy = np.ceil(base_xy)

        base_xz = base_x - base_z
        base_xz = np.ceil(base_xz)

        base_zx = base_z - base_x
        base_zx = np.ceil(base_zx)

        base_x = np.ceil(base_x)
        base_y = np.ceil(base_y)
        base_z = np.ceil(base_z)

        lenx = matrix.shape[0]
        leny = matrix.shape[1]
        lenz = matrix.shape[2]

        matrix = self.expand(matrix)

        for x in range(matrix.shape[0]):
            for y in range(matrix.shape[1]):
                for z in range(matrix.shape[2]):
                    if np.dot(base_x, np.array([x - lenx*base_x[0]*3/2, y - leny*base_x[1]*3/2, z - lenz*base_x[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_x, np.array([x - lenx*base_x[0]*1/2, y - leny*base_x[1]*1/2, z - lenz*base_x[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

                    if np.dot(base_y, np.array([x - lenx*base_y[0]*3/2, y - leny*base_y[1]*3/2, z - lenz*base_y[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_y, np.array([x - lenx*base_y[0]*1/2, y - leny*base_y[1]*1/2, z - lenz*base_y[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

                    if np.dot(base_z, np.array([x - lenx*base_z[0]*3/2, y - leny*base_z[1]*3/2, z - lenz*base_z[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_z, np.array([x - lenx*base_z[0]*1/2, y - leny*base_z[1]*1/2, z - lenz*base_z[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

                    if np.dot(base_xy, np.array([x - lenx*base_xy[0]*3/2, y - leny*base_xy[1]*3/2, z - lenz*base_xy[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_xy, np.array([x - lenx*base_xy[0]*1/2, y - leny*base_xy[1]*1/2, z - lenz*base_xy[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

                    if np.dot(base_xz, np.array([x - lenx*base_xz[0]*3/2, y - leny*base_xz[1]*3/2, z - lenz*base_xz[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_xz, np.array([x - lenx*base_xz[0]*1/2, y - leny*base_xz[1]*1/2, z - lenz*base_xz[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

                    if np.dot(base_zx, np.array([x - lenx*base_zx[0]*3/2, y - leny*base_zx[1]*3/2, z - lenz*base_zx[2]*3/2])) >= 0:
                        matrix[x, y, z] = 1
                    if np.dot(-base_zx, np.array([x - lenx*base_zx[0]*1/2, y - leny*base_zx[1]*1/2, z - lenz*base_zx[2]*1/2])) >= 0:
                        matrix[x, y, z] = 1

        return matrix

    def expand(self, matrix):
        '''
        Expands given matrix 4 quadrents

        Parameters
        ------

        matrix: numpy.array
            3D Matrix should represent reciprocal lattice

        Return
        ------

            Expanded matrix
        '''
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
        '''
        Reads hdf_file set in self.filename,
        normalises the data and translates it to an *Inviwo-Volum*

        Additional options to expand the data and to translate the data to
        brillouin zone are possible through the *Inviwo-properties*

        Returns
        -------

        None
        '''
        if len(self.filename.value) == 0 or not Path(self.filename.value).exists():
            return

        band_index = self.energy_band.value
        with h5py.File(self.filename.value, 'r') as f:
            basis = f.get('reciprocal_basis')[()]
            fermi_energy = f.get('fermi_energy')[()]

            matrix = f.get('fermi_bands').get(str(band_index)).get('composition')[()]

            self.energy_band.minValue = 0
            self.energy_band.maxValue = len(f.get('fermi_bands')) - 1

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

        normal_fermi_energy = normalize(fermi_energy)
        if normal_fermi_energy and 0 < normal_fermi_energy and normal_fermi_energy < 1:
            self.fermi_level.value = 0
            self.fermi_level.value = normal_fermi_energy

        print('E-Fermi: {}'.format(fermi_energy))
        print('E-Fermi Normal: {}'.format(normalize(fermi_energy)))
        print('E-Min: {}'.format(emax))
        print('E-Max: {}'.format(emin))

        self.volumeOutport.setData(volumes)

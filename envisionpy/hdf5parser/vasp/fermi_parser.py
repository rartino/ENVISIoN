#
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

from pathlib import Path
import h5py
import numpy as np
import re
import sys
import scipy

def enlarge(matrix):
    '''
    Inviwo requires volume data to be at least 48x48x48 in size. 
    Interpolate volume data voxels until that size is reached.
    '''

    # Inviwo requires arrays to be above a certain size.
    # Volumes in hdf5 below 48x48x48 will not be detected
    # Larger interpolated volume dimensions make slice look better. 
    # 128 seem to be a good choice between size and looks.
    scale = 128/min(len(x) for x in matrix)
    if scale > 1:
        matrix = scipy.ndimage.zoom(matrix, scale, None, 3, 'wrap')

    # while any(len(x) < 96 for x in matrix):
    #     matrix = scipy.ndimage.zoom(matrix, 2)
    return matrix

def expand(matrix):
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

def brillouin_zone(matrix, basis):
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

        matrix = expand(matrix)

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

def convert_fermi_volumes(band, basis, fermi_energy):
    emin = band.min()
    emax = band.max()
    def normalize(value):
            return (value - emin) / (emax - emin)
    normalize_vector = np.vectorize(normalize)

    fermi_matrix = normalize_vector(band.copy())
    brillouin_zone_matrix = brillouin_zone(fermi_matrix.copy(), basis)
    expanded_matrix = expand(fermi_matrix.copy())
    normalized_fermi_energy = normalize(fermi_energy)

    fermi_matrix = enlarge(fermi_matrix)
    brillouin_zone_matrix = enlarge(brillouin_zone_matrix)
    expanded_matrix = enlarge(expanded_matrix)


    # fermi_matrix = expand(fermi_matrix)
    # brillouin_zone_matrix = expand(brillouin_zone_matrix)
    # fermi_matrix = expand(fermi_matrix)
    # fermi_matrix = expand(fermi_matrix)
    return [fermi_matrix, brillouin_zone_matrix, expanded_matrix, normalized_fermi_energy]


def fermi_parser(hdf_file_path, vasp_dir_path):
    """
    Reads OUTCAR and EIGNVAL to create datastructure for visualization of fermi surfaces

    Parameters
    ----------
    hdf_file_path: str
        Path where hdf file will be written to
    vasp_dir_path: str
        Path of direcotry containing OUTCAR and EIGENVAL files

    Returns
    -------
    None
    """
    # Check for files
    # ---------------
    outcar_file_path = Path(vasp_dir_path).joinpath('OUTCAR')
    eigenval_file_path = Path(vasp_dir_path).joinpath('EIGENVAL')

    if not outcar_file_path.exists() or not eigenval_file_path.exists():
        raise FileNotFoundError('Cannot find one of the two vasp files in directory %s' % vasp_dir_path)

    # Parse OUTCAR file for fermi energy and reciprocal lattice vectors
    # https://www.vasp.at/wiki/index.php/OUTCAR
    # --------------------------------------------------------------
    with outcar_file_path.open('r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            if 'E-fermi' in line:
                fermi_energy = float(re.findall(r'-?[\d.]+', line)[0])

            if 'reciprocal lattice vectors' in line:
                base_x = re.findall(r'-?[\d.]+', lines[i + 1])[3:]
                base_x = [float(x) for x in base_x]

                base_y = re.findall(r'-?[\d.]+', lines[i + 2])[3:]
                base_y = [float(x) for x in base_y]

                base_z = re.findall(r'-?[\d.]+', lines[i + 3])[3:]
                base_z = [float(x) for x in base_z]

    basis = np.array([base_x, base_y, base_z])

    # Parse EIGENVAL file for all calculated K-Points and band energies
    # https://www.vasp.at/wiki/index.php/EIGENVAL
    # ----------------------------------------------------------------
    with eigenval_file_path.open('r') as f:
        lines = f.readlines()

        # collect meta data
        [_, _, _, nspin] = [int(v) for v in re.findall(r'[\d]+', lines[0])]
        nelectrons, nkpoints, nbands = [int(v) for v in re.findall(r'[\d]+', lines[5])]

        kpoints = np.zeros(shape=(nkpoints, 4))
        evalues = np.zeros(shape=(nkpoints, nbands, nspin), dtype=np.float32)

        kpoint_index = 0
        for i, line in enumerate(lines[7:]):
            regex = re.findall(r'[-\d.E+]+', line)

            # kpoint
            if len(regex) == 4:
                kpoints[kpoint_index, :] = [float(v) for v in regex]
                kpoint_index += 1

            # eigenvalue
            elif len(regex) > 0:
                band_index = int(regex[0])
                values = [float(v) for v in regex[1:1+nspin:]]
                evalues[kpoint_index - 1, band_index - 1, :] = values

    # derive dimensions from unique kpoints
    nkpoints_x = len(set(kpoints[:, 0]))
    nkpoints_y = len(set(kpoints[:, 1]))
    nkpoints_z = len(set(kpoints[:, 2]))

    # Write data to HDF5
    # ------------------
    hdf_file = h5py.File(hdf_file_path, 'a')
    hdf_file.create_dataset('fermi_energy', data=np.array(fermi_energy))
    hdf_file.create_dataset('reciprocal_basis', data=basis)

    hdf_group = hdf_file.create_group('fermi_bands')
    for band_index in range(nbands):
        band = np.reshape(evalues[:, band_index, 0], (nkpoints_x, nkpoints_y, nkpoints_z))

        hdf_subgroup = hdf_group.create_group(str(band_index))
        hdf_subgroup.create_dataset('composition', data=band, dtype='float32')

        volumes = convert_fermi_volumes(band, basis, fermi_energy)
        hdf_subgroup.create_dataset('fermi_volume', data=volumes[0], dtype=np.float32)
        hdf_subgroup.create_dataset('brillouin_zone', data=volumes[1], dtype=np.float32)
        hdf_subgroup.create_dataset('expanded_volume', data=volumes[2], dtype=np.float32)
        hdf_subgroup.create_dataset('normalized_fermi_energy', data=np.array(volumes[3]), dtype=np.float32)

    hdf_file.close()

    return True


if __name__ == '__main__':
    fermi_parser(sys.argv[1], sys.argv[2])

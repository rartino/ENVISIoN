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
import h5py
import numpy as np
import re
import sys


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

    hdf_file.close()


if __name__ == '__main__':
    fermi_parser(sys.argv[1], sys.argv[2])

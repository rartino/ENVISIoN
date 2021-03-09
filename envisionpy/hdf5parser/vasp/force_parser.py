import h5py
import numpy as np
import re
import sys
import scipy
import timeit
from pathlib import Path
import sys, os, inspect
import os, sys, inspect


def force_parser(hdf_file_path, vasp_dir_path):
    """
    Comments
    """
    forces = []
    force_position = []
    pos = 0
    amount = 0
    outcar_file_path = Path(vasp_dir_path).joinpath('OUTCAR')
    if not outcar_file_path.exists():
        raise FileNotFoundError('Cannot find the vasp file in directory %s'
                                % vasp_dir_path)
    with outcar_file_path.open('r') as f:

        lines = f.readlines()
        for n, line in enumerate(lines):
            if 'total drift' in line:
                pos = n - 2
        for i, line in enumerate(lines):
            if 'reciprocal lattice vectors' in line:
                base_x = re.findall(r'-?[\d.]+', lines[i + 1])[3:]
                base_x = [float(x) for x in base_x]
                base_y = re.findall(r'-?[\d.]+', lines[i + 2])[3:]
                base_y = [float(x) for x in base_y]
                base_z = re.findall(r'-?[\d.]+', lines[i + 3])[3:]
                base_z = [float(x) for x in base_z]
                basis = np.array([base_x, base_y, base_z])
            if 'POSITION' in line:
                k = i + 1
                while k < pos:
                    force = (re.findall(r'-?[\d.]+', lines[k + 1])[3:])
                    force = [float(x) for x in force]
                    forces.append(force)
                    position = (re.findall(r'-?[\d.]+', lines[k + 1])[:3])
                    position = [float(x) for x in position]
                    force_position.append(position)
                    k += 1
    amount = len(forces)
    try:
        hdf_file = h5py.File(hdf_file_path, 'a')
        hdf_file.create_dataset('reciprocal_basis', data=basis)
        hdf_file.create_dataset('forces', data=forces)
        hdf_file.create_dataset('force position', data=force_position)
        hdf_file.close()
        print("Succesfully written data to HDF5-file")
    except:
        print("Failed to write to HDF5-file")

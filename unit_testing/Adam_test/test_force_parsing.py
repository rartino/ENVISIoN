import h5py
import numpy as np
import re
import sys
import scipy
import timeit
from pathlib import Path
import sys, os, inspect
import os, sys, inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
VASP_DIR = path_to_current_folder + "/resource"


start = timeit.default_timer()

def _get_co_and_int(file_path, co_start, to_amount):
    coordinate_start = co_start
    initial_velocity_start = co_start + to_amount + 1
    total_amount = to_amount
    with file_path.open('r') as f:
        lines = f.readlines()
        coordinates = get_data(total_amount,  lines, coordinate_start)
        initial_velocity = get_data(total_amount,  lines, initial_velocity_start)
    return  [coordinates, initial_velocity]

def total_amount(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        atom_amount = lines[6].split()
        total_amount = 0
        for i in atom_amount:
            total_amount += int(i)
    return [atom_amount, total_amount]

def atom_names(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        atom_names = lines[5].split()
    return atom_names

def get_basis(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        base_x = np.float32(lines[2].split())
        base_y = np.float32(lines[3].split())
        base_z = np.float32(lines[4].split())
    return np.array([base_x, base_y, base_z])

def get_data(amount, data, start):
    n = 0
    list = []
    while n < amount:
        current = []
        line = data[start+n].split()
        current.append(np.float32(line[0]))
        current.append(np.float32(line[1]))
        current.append(np.float32(line[2]))
        list.append(current)
        n += 1
    return list

def write_hdf(hdf_file, datas, base):
    try:
        with h5py.File(hdf_file, 'a') as hdf_file:
            if "coordinates" and "initial_velocity" and "basis" in hdf_file:
                del hdf_file["coordinates"]
                del hdf_file["initial_velocity"]
                del hdf_file["basis"]
            hdf_file.create_dataset("coordinates", data=np.array(datas[0]))
            hdf_file.create_dataset("initial_velocity", data=np.array(datas[1]))
            hdf_file.create_dataset("basis", data = base)
            hdf_file.close()

    except:
        print("Error in reading POSCAR-file or writing HDF5")

def force_parser(hdf_file, vasp_dir_path):
    """
    Comments
    """
    poscar_file_path = Path(vasp_dir_path).joinpath('POSCAR')
    if not poscar_file_path.exists():
        raise FileNotFoundError('Cannot find the vasp file in directory %s' % vasp_dir_path)

    [coordinates, initial_velocity] = _get_co_and_int(poscar_file_path,8 ,int(total_amount(poscar_file_path)[1]))
    base = get_basis(poscar_file_path)
    write_hdf(hdf_file, [coordinates, initial_velocity], base)

force_parser("farce.hdf5", VASP_DIR)

stop = timeit.default_timer()
#write_hdf("POSCAR")

print('Time: ', float(stop - start), " seconds")

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
VASP_DIR2 = path_to_current_folder + "/resource"

def _get_co_and_int(file_path, co_start, to_amount):
    coordinate_start = co_start
    initial_velocity_start = co_start + to_amount + 1
    total_amount = to_amount
    with file_path.open('r') as f:
        lines = f.readlines()
        coordinates = _get_data(total_amount,  lines, coordinate_start)
        initial_velocity = _get_data(total_amount,  lines, initial_velocity_start)
    return  [coordinates, initial_velocity]

def _total_amount(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        atom_amount = lines[6].split()
        total_amount = 0
        for i in atom_amount:
            total_amount += int(i)
    return [atom_amount, total_amount]

def _get_names(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        atom_names = lines[5].split()
    return atom_names

def _get_basis(file_path):
    with file_path.open('r') as f:
        lines = f.readlines()
        base_x = np.float32(lines[2].split())
        base_y = np.float32(lines[3].split())
        base_z = np.float32(lines[4].split())
    return np.array([base_x, base_y, base_z])

def _get_data(amount, data, start):
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

def _write_hdf(hdf_file, datas, base, names, amount):
    try:
        hf = h5py.File(hdf_file, 'a')
        hdf_group = hf.create_group("group_1")
        hdf_group.create_dataset("coordinates", data=np.array(datas[0]))
        hdf_group.create_dataset("initial_velocity", data=np.array(datas[1]))
        hdf_group.create_dataset("basis", data = base)
        asciiList = [n.encode("ascii", "ignore") for n in names]
        hdf_group.create_dataset('names', (len(asciiList),1),'S10', asciiList)
        hdf_group.create_dataset("amount", data = np.array(amount))
        hf.close()
        print("Data written to HDF5")
    except:
        print("Error in writing to HDF5")

def force_parser(hdf_file, vasp_dir_path):
    """
    Comments
    """
    poscar_file_path = Path(vasp_dir_path).joinpath('POSCAR')
    if not poscar_file_path.exists():
        raise FileNotFoundError('Cannot find the vasp file in directory %s'
                                % vasp_dir_path)
    amount = int(_total_amount(poscar_file_path)[1])
    try:
        [coordinates, initial_velocity] = _get_co_and_int(poscar_file_path,8
                                      ,amount)
        print("Coordinates and velocities succesfully parsed")
        base = _get_basis(poscar_file_path)
        print("Basis succesfully parsed")
        names = _get_names(poscar_file_path)
        print("Names succesfully parsed")
        _write_hdf(hdf_file, [coordinates, initial_velocity], base, names, amount)

    except:
        print("Error in reading POSCAR")

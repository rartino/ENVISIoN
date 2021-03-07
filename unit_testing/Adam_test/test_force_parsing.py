import h5py
import numpy as np
import re
import sys
import scipy
import timeit

start = timeit.default_timer()

def test_atom(POSCAR):
    coordinate_start = 8
    initial_velocity_start = 137
    n = 0
    n2 = 0
    with open(POSCAR, 'r') as f:
        lines = f.readlines()
        atom_names = lines[5].split()
        atom_amount = lines[6].split()
        total_amount = 0
        for i in atom_amount:
            total_amount += int(i)
        coordinates = get_data(total_amount,  lines, coordinate_start)
        initial_velocity = get_data(total_amount,  lines, initial_velocity_start)
    return  [atom_names, atom_amount, total_amount, coordinates, initial_velocity]

def get_basis(POSCAR):
    with open(POSCAR, 'r') as f:
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

def write_hdf(VASP_FILE):
    try:
        datas = test_atom(VASP_FILE)
        base = get_basis(VASP_FILE)
        with h5py.File("FORCE.hdf5", 'a') as hdf_file:
            if "coordinates" and "initial_velocity" and "basis" in hdf_file:
                del hdf_file["coordinates"]
                del hdf_file["initial_velocity"]
                del hdf_file["basis"]
            hdf_file.create_dataset('coordinates', data=np.array(datas[3]))
            hdf_file.create_dataset('initial_velocity', data=np.array(datas[4]))
            hdf_file.create_dataset("basis", data = base)
            hdf_file.close()

    except:
        print("Error in reading POSCAR-file or writing HDF5")


stop = timeit.default_timer()
write_hdf("POSCAR")

print('Time: ', float(stop - start), " seconds")

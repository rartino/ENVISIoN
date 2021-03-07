import h5py
import numpy as np
import re
import sys
import scipy
import timeit

start = timeit.default_timer()

def test_atom():
    coordinate_start = 8
    initial_velocity_start = 137
    n = 0
    n2 = 0
    with open("POSCAR", 'r') as f:
        lines = f.readlines()
        atom_names = lines[5].split()
        atom_amount = lines[6].split()
        total_amount = 0
        for i in atom_amount:
            total_amount += int(i)
        coordinates = get_data(total_amount,  lines, coordinate_start)
        initial_velocity = get_data(total_amount,  lines, initial_velocity_start)
    return  [atom_names, atom_amount, total_amount, coordinates, initial_velocity]
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
stop = timeit.default_timer()
print(test_atom())
print('Time: ', float(stop - start), " seconds")

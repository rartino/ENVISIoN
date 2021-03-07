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
    coordinates = []
    initial_velocity = []
    n = 0
    n2 = 0
    with open("POSCAR", 'r') as f:
        lines = f.readlines()
        atom_names = lines[5].split()
        atom_amount = lines[6].split()
        total_amount = 0
        for i in atom_amount:
            total_amount += int(i)
        while n < total_amount:
            current = []
            current.append(float(lines[coordinate_start+n].split()[0]))
            current.append(float(lines[coordinate_start+n].split()[1]))
            current.append(float(lines[coordinate_start+n].split()[2]))
            coordinates.append(current)
            n += 1
        while n2 < total_amount:
            print(n2)
            current = []
            current.append(float(lines[initial_velocity_start+n2].split()[0]))
            current.append(float(lines[initial_velocity_start+n2].split()[1]))
            current.append(float(lines[initial_velocity_start+n2].split()[2]))
            initial_velocity.append(current)
            n2 += 1
        return  [atom_names, atom_amount, total_amount, coordinates, initial_velocity]
stop = timeit.default_timer()
print(test_atom())
print('Time: ', float(stop - start), " seconds")

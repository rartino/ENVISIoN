import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import h5py
from h5writer import _write_basis, _write_scaling_factor, _write_coordinates, _write_forces
from pathlib import Path
path = '/home/labb/ENVISIoN/ENVISIoN/envisionpy/hdf5parser/ELK'
sys.path.insert(0, os.path.expanduser(path))
from unitcell_parser import unitcell_parser, find_elements, parse_coordinates

def check_directory_force_elk(vasp_path):
    if Path(vasp_path).joinpath('INFO.OUT').exists() and Path(vasp_path).joinpath('EQATOMS.OUT').exists():
        with Path(vasp_path).joinpath('INFO.OUT').open('r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'Forces' in line:
                    return True
    return False


def parse_force(elk_dir, coordinates):
    forces = []
    force_tips = []
    with Path(elk_dir).joinpath('INFO.OUT').open('r') as f:
        lines = f.readlines()
    for line in lines:
        if "total force" in line:
            new_force = []
            line_list = line.replace("\n", "").split()
            for x in range(len(line_list)):
                if re.match(r"^[+-]?\d(>?\.\d+)?$", line_list[x]) is not None:
                    new_force += [float(line_list[x])]
            forces += [new_force]
    for i in range(len(forces)):
        list = [x + y for x, y in zip(coordinates[i], forces[i])]
        for p in coordinates[i]:
            list.append(p)
        force_tips.append(list)
    return force_tips


def parse_force_elk(h5file, elk_dir, inviwo = False, elements=None):
    elements, atoms = find_elements(elk_dir)
    coordinates = parse_coordinates(elk_dir, atoms)
    force_tips = parse_force(elk_dir, coordinates)
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if "/UnitCell" not in h5:
                unitcell_parser(h5file, elk_dir)
        _write_forces(h5file,
        atoms,
        force_tips,
        '/Forces')
        return True
    else:
        unitcell_parser(h5file, elk_dir)
        _write_forces(h5file,
        atoms,
        force_tips,
        '/Forces')
        return True

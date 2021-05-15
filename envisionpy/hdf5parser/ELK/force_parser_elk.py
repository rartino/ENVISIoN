##  ENVISIoN
##
##  Copyright (c) 2021 Gabriel Anderberg, Didrik Axén, Adam Engman,
##  Kristoffer Gubberud Maras, Joakim Stenborg
##  All rights reserved.
##
##  Redistribution and use in source and binary forms, with or without
##  modification, are permitted provided that the following conditions are met:
##
##  1. Redistributions of source code must retain the above copyright notice, this
##  list of conditions and the following disclaimer.
##  2. Redistributions in binary form must reproduce the above copyright notice,
##  this list of conditions and the following disclaimer in the documentation
##  and/or other materials provided with the distribution.
##
##  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
##  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
## ##############################################################################################

import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import h5py
from h5writer import _write_basis, _write_scaling_factor, _write_coordinates, _write_forces
from pathlib import Path
#path = '/home/labb/ENVISIoN/ENVISIoN/envisionpy/hdf5parser/ELK'
#sys.path.insert(0, os.path.expanduser(path))
#from unitcell_parser import unitcell_parser, find_elements, parse_coordinates

def check_directory_force_elk(vasp_path):
    if Path(vasp_path).joinpath('INFO.OUT').exists() and Path(vasp_path).joinpath('EQATOMS.OUT').exists():
        with Path(vasp_path).joinpath('INFO.OUT').open('r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'Forces' in line:
                    return True
    return False


def find_elements( ELK_dir):
    elements = []
    number_of_atoms = []
    with open(os.path.join(ELK_dir,"EQATOMS.OUT"), "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Species" in line:
                list_of_word_in_line = line.split()
                for word in list_of_word_in_line:
                    if "(" in word:
                        word = word.replace("(","")
                        word = word.replace(")","")
                        elements += [word]
                list_of_word_in_line = lines[i+2].split()
                number_of_atoms += [len(list_of_word_in_line)]
    return elements, number_of_atoms

def parse_lattice(ELK_dir):
    basis = []
    with open(os.path.join(ELK_dir,'INFO.OUT'), "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Lattice vectors :" in line:
                basis.append([float(n) for n in lines[i+1].split()[:3]])
                basis.append([float(n) for n in lines[i+2].split()[:3]])
                basis.append([float(n) for n in lines[i+3].split()[:3]])
            if "Unit cell volume      :" in line:
                list = line.split()
                scaling_factor = -float(list[-1])
    return scaling_factor ,basis

def parse_coordinates(ELK_dir, number_of_atoms):
    coords_list = []
    with open(os.path.join(ELK_dir,'INFO.OUT'), "r") as f:
        lines = f.readlines()
        counter = 0
        for i, line in enumerate(lines):
            if "atomic positions" in line:
                n = 0
                while n < number_of_atoms[counter]:
                    list_of_line = lines[i+1+n].split()[2:5]
                    coords_list += [list_of_line]
                    n += 1
                counter += 1
        for x in range(len(coords_list)):
            for y in range(len(coords_list[x])):
                coords_list[x][y] = float(coords_list[x][y])
    return coords_list


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
    scaling_factor, basis = parse_lattice(elk_dir)
    force_tips = parse_force(elk_dir, coordinates)
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if "/UnitCell" not in h5:
                _write_basis(h5file, basis)
                _write_scaling_factor(h5file, scaling_factor = 1)
                _write_coordinates(
                    h5file,
                    atoms,
                    coordinates,
                    elements,
                    '/UnitCell'
                )
        _write_forces(h5file,
        atoms,
        force_tips,
        '/Forces')
        return True
    else:
        _write_basis(h5file, basis)
        _write_scaling_factor(h5file, scaling_factor = 1)
        _write_coordinates(
            h5file,
            atoms,
            coordinates,
            elements,
            '/UnitCell'
        )
        _write_forces(h5file,
        atoms,
        force_tips,
        '/Forces')
        return True

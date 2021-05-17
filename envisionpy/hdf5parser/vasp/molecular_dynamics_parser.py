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
from h5writer import _write_md
from pathlib import Path
# Define coordinates regex.
coordinates_re = re.compile(r' +'.join([r'([+-]?[0-9]+\.[0-9]+)'] * 3))

def _find_line(rgx, f):
    match = None
    while not match:
        match = rgx.search(next(f))
    return match

def get_coordinates_for_time_step(lines):
    return_list = []
    for i, line in enumerate(lines):
        line_list = list(line.split(" "))
        new_line_list = []
        for x in range(len(line_list)):
            if line_list[x] != "":
                new_line_list.append(line_list[x])
        line_list = new_line_list
        for x in range(len(line_list)):
            line_list[x] = float(line_list[x])
        return_list.append(line_list)
    return return_list

def _parse_potcar(potcar_file):
    # Look for elements in POTCAR
    elements = []
    with open(potcar_file, "r") as f:
        element_re = re.compile('TITEL.*')
        match = None
        for line in f:
            match = element_re.search(line)
            if match:
                elements.append(match.group().split()[3].split('_')[0])
    return elements

def _find_elements(fileobj, elements, vasp_dir):
    atomcount_re=re.compile('^ *(([0-9]+) *)+$')
    last_comment = None
    poscar_elements = []
    while True:
        atoms_per_species = next(fileobj)
        match = atomcount_re.match(atoms_per_species)
        if match:
            break
        last_comment = atoms_per_species
    if last_comment:
        poscar_elements = last_comment.split()
    # Number of atoms
    atoms = [int(n) for n in atoms_per_species.split()]
    # Parses number of atoms per species from POTCAR
    if not elements:
        try:
            elements = _parse_potcar(os.path.join(vasp_dir, 'POTCAR'))
        except FileNotFoundError:
            elements = poscar_elements
    if not elements:
        raise Exception('Element symbols not found.')
    if len(elements) != len(atoms):
        raise Exception('Incorrect number of elements.')
    return elements, atoms

def check_directory_molecular_dynamics_parser(vasp_path):
    if Path(vasp_path).joinpath('OUTCAR').exists() and Path(vasp_path).joinpath('XDATCAR').exists() and Path(vasp_path).joinpath('POSCAR').exists():
        with Path(vasp_path).joinpath('OUTCAR').open('r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 'IBRION' in line:
                    line_list_IBRION = list(line.split(" "))
                    new_line_list_IBRION = []
                    for x in range(len(line_list_IBRION)):
                        if line_list_IBRION[x] != "":
                            new_line_list_IBRION.append(line_list_IBRION[x])
                    line_list_IBRION = new_line_list_IBRION
                    break
            if line_list_IBRION[2] == "0":
                return True
            else:
                return False
    else:
        return False

def mol_dynamic_parser(hdf5_file_path, vasp_dir_path, elements=None):
    if os.path.isfile(hdf5_file_path):
        with h5py.File(hdf5_file_path, 'r') as h5:
            if "/MD" in h5:
                print("Already parsed. Skipping.")
                return True
    has_md_ok = False
    time_step = 0
    outcar_file_path = Path(vasp_dir_path).joinpath('OUTCAR')
    xdatcar_file_path = Path(vasp_dir_path).joinpath('XDATCAR')
    poscar_file_path = Path(vasp_dir_path).joinpath('POSCAR')

    if not outcar_file_path.exists() or not xdatcar_file_path.exists()or not poscar_file_path.exists():
        raise FileNotFoundError('Cannot find one of the three vasp files in directory')

    with outcar_file_path.open('r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # if 'IBRION' in line:
            #     line_list_IBRION = list(line.split(" "))
            #     new_line_list_IBRION = []
            #     for x in range(len(line_list_IBRION)):
            #         if line_list_IBRION[x] != "":
            #             new_line_list_IBRION.append(line_list_IBRION[x])
            #     line_list_IBRION = new_line_list_IBRION
            if "NSW" in line:
                line_list_NSW = list(line.split(" "))
                new_line_list_NSW = []
                for x in range(len(line_list_NSW)):
                    if line_list_NSW[x] != "":
                        new_line_list_NSW.append(line_list_NSW[x])
                line_list_NSW = new_line_list_NSW
                break
        # if line_list_IBRION[2] == "0":
        #     has_md_ok = True
        time_steps = int(line_list_NSW[2])
        f.close()

    #if has_md_ok is True:
    with poscar_file_path.open("r") as f:
        elements, atoms = _find_elements(f, elements, vasp_dir_path)
        f.close()

    with xdatcar_file_path.open('r') as f:
        lines = f.readlines()
        coordinates_list = []
        for i, line in enumerate(lines):
            if 'Direct configuration' in line:
                coordinates_list = get_coordinates_for_time_step(lines[i+1:i+sum(atoms)+1])
                _write_md(hdf5_file_path, atoms, coordinates_list, elements, time_step)
                time_step += 1
        f.close()

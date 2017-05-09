#
#  ENVISIoN
#
#  Copyright (c) 2017 Josef Adamsson
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

import os
import re
import h5py
from ..h5writer import _write_unitcell

# Define coordinates regex.
coordinates_re = re.compile(r' +'.join([r'(-?[0-9]+\.[0-9]+)'] * 3))

def _find_line(rgx, f):
    match = None
    while not match:
        match = rgx.search(next(f))
    return match

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

def _parse_lattice(f):
    # Read header.
    header = next(f)

    # Read scaling factor
    scaling_factor = float(next(f))

    # Read lattice vectors
    basis = []
    basis.append([float(n) for n in next(f).split()])
    basis.append([float(n) for n in next(f).split()])
    basis.append([float(n) for n in next(f).split()])

    # Atom species
    atomcount_re=re.compile('^ *(([0-9]+) *)+$')
    last_comment = None
    elements = []
    while True:
        atoms_per_species = next(f)
        match = atomcount_re.match(atoms_per_species)
        if match:
            break
        last_comment = atoms_per_species
    if last_comment:
        elements = last_comment.split()   

    # Number of atoms
    atom_count = [int(n) for n in atoms_per_species.split()]
    if len(elements) != len(atom_count):
        elements = []

    # Cartesian or direct coordinates
    coord_re = re.compile(r'^[cCkKdD]')
    coord_type = _find_line(coord_re,f)
    if (coord_type.group() == 'd') or (coord_type.group() == 'D'):
        cartesian = False
    else:
        cartesian = True

    return {'header'         : header,
            'scaling_factor' : scaling_factor,
            'basis'          : basis, 
            'atom_count'     : atom_count,
            'elements'       : elements,
            'cartesian'      : cartesian}
            

def _parse_coordinates(f,count):
    match = _find_line(coordinates_re, f)
    try:
        coords_list = []
        while match:
            coords = [float(coordinate) for coordinate in match.groups()]
            coords_list.append(coords)
            match = coordinates_re.search(next(f))
    except StopIteration:
        pass # if EOF is reached here
    
    if len(coords_list) != count:
        raise Exception('Incorrect number of coordinates.')

    return coords_list

def _find_elements(elements, poscar_elements, vasp_dir, n_species):
    if not elements:
        try:
            elements = _parse_potcar(os.path.join(vasp_dir, 'POTCAR'))
        except FileNotFoundError:
            elements = poscar_elements
             
    if not elements:
        raise Exception('Element symbols not found.')

    if len(elements) != n_species:
        raise Exception('Incorrect number of elements.')
    return elements

    
def unitcell(h5file, vasp_dir, elements=None):
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if "/UnitCell" in h5:
                print("Already parsed. Skipping.")
                return False
        
    try:
        with open(os.path.join(vasp_dir,'POSCAR'), "r") as f:
            pdata = _parse_lattice(f)
            elements = _find_elements(elements, pdata['elements'], vasp_dir, len(pdata['atom_count']))
            coords_list = _parse_coordinates(f,sum(pdata['atom_count']))
            _write_unitcell(h5file,
                            pdata['scaling_factor'],
                            pdata['basis'], 
                            pdata['atom_count'], 
                            coords_list, 
                            elements, 
                            pdata['cartesian'])
            return True
    except FileNotFoundError:
        print("POSCAR file not found.")
        return False


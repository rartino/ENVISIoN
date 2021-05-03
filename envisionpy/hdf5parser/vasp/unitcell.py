"""Functions for parsing lattice vecors, unit cell data from POSCAR
and element symbols from POTCAR.

"""

#
#  ENVISIoN
#
#  Copyright (c) 2017-2018 Josef Adamsson, Marian Brännvall, Anders Rehult
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
##############################################################################################
#
#  Alterations to this file by Anders Rehult, Marian Brännvall, Anton Hjert
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import h5py
from pathlib import Path
from h5writer import _write_basis, _write_scaling_factor, _write_coordinates

# Define coordinates regex.
coordinates_re = re.compile(r' +'.join([r'([+-]?[0-9]+\.[0-9]+)'] * 3))

def _find_line(rgx, f):
    match = None
    while not match:
        match = rgx.search(next(f))
    return match

def _parse_potcar(potcar_file):
    """Looks for element symbols in POTCAR

    Parameters
    ----------
    potcar_file : str
        Path to POTCAR file

    Returns
    -------
    elements : list of str
        List of element symbols
    """
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

def _parse_lattice(fileobj):
    """Reads lattice vectors

    Returns scaling factor and lattice vectors. First line is ignored.

    Parameters
    ----------
    fileobj : file object
        File to be parsed

    Returns
    -------
    scaling_factor: float
    ndarray
        3x3 matrix
    """
    # Read header.
    header = next(fileobj)

    # Read scaling factor
    scaling_factor = float(next(fileobj).split()[0])

    # Read lattice vectors
    basis = []
    basis.append([float(n) for n in next(fileobj).split()[:3]])
    basis.append([float(n) for n in next(fileobj).split()[:3]])
    basis.append([float(n) for n in next(fileobj).split()[:3]])

    return scaling_factor, np.array(basis)

def _cartesian(fileobj):
    """Checks if positions are given as cartesian coordinates

    Parameters
    ----------
    fileobj : file object
        File to be parsed

    Returns
    -------
    bool
        True if coordinates are cartesian
    """
    # Cartesian or direct coordinates
    coord_re = re.compile(r'^[cCkKdD]')
    coord_type = _find_line(coord_re,fileobj)
    if (coord_type.group() == 'd') or (coord_type.group() == 'D'):
        return False
    else:
        return True


def _parse_coordinates(fileobj, count, transform=False, matrix=None):
    """Reads coordinates from file and transforms them

    Parameters
    ----------
    fileobj : file object
        File to be parsed

    count : int
        Expected number of coordinates

    transform : bool
         (Default value = False)
        If True, coordinates will be transformed

    matrix : ndarray
         (Default value = None)
        3x3 matrix used to transform coordinates

    Returns
    -------
    coords_list : list of float
        List of coordinates
    """
    match = False
    try:
        coords_list = []
        match = _find_line(coordinates_re, fileobj)
        while match:
            coords = [float(coordinate) for coordinate in match.groups()]
            if transform:
                coords = np.dot(matrix, coords)
            coords_list.append(coords)
            match = coordinates_re.search(next(fileobj))
    except StopIteration:
        pass # if EOF is reached here

    if len(coords_list) != count:
        raise Exception('Incorrect number of coordinates.', len(coords_list))

    return coords_list

def _find_elements(fileobj, elements, vasp_dir):
    """Finds the number of atoms per species and corresponding symbols

    Reads the number of atoms per species and looks for corresponding element symbols.
    If no list is given, the POTCAR file is used. If no POTCAR is found, the parsed
    file is assumed to contain a comment with symbols.
    If the correct number of symbols was not found, an exceptions is raised.

    Parameters
    ----------
    fileobj : file object
        File to be parsed

    elements : list of str
        Element symbols

    vasp_dir : str
        Path to directory containing POTCAR

    Returns
    -------
    elements : list of str
        Element symbols
    atoms : list of int
        Number of atoms per species
    """
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

def check_directory_unitcell(vasp_path):
	if Path(vasp_path).joinpath('POTCAR').exists() and Path(vasp_path).joinpath('POSCAR').exists():
		return True
	else:
		return False


def unitcell(h5file, vasp_dir, elements=None, poscar_equiv='POSCAR'):
    """POSCAR parser

    Reads lattice vectors and atom positions from POSCAR file and writes data to an HDF5 file.
    If no element symbols are given as an argument, the parser looks for them in the POTCAR file,
    or in POSCAR if no POTCAR file is found.
    If POSCAR uses cartesian coordinates, they will be transformed.
    If the given HDF5 file already contains unit cell data, nothing is parsed.

    Parameters
    ----------
    h5file : str
        Path to HDF5 file

    vasp_dir : str
        Path to directory containing POSCAR file

    elements : list of str
         (Default value = None)
        List of element symbols

    Returns
    -------
    bool
        True if POSCAR was parsed, False otherwise.
    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if "/UnitCell" in h5:
                print("Already parsed. Skipping.")
                return True

    try:
        # Parses lattice vectors and atom positions from POSCAR
        with open(os.path.join(vasp_dir,poscar_equiv), "r") as f:
            scaling_factor, basis = _parse_lattice(f)
            elements, atoms = _find_elements(f, elements, vasp_dir)
            coords_list = _parse_coordinates(
                f,
                sum(atoms),
                _cartesian(f),
                np.linalg.inv(basis)
            )
            _write_basis(h5file, basis)
            _write_scaling_factor(h5file, scaling_factor)
            _write_coordinates(
                h5file,
                atoms,
                coords_list,
                elements,
                '/UnitCell'
            )
            return True
    except FileNotFoundError:
        print("POSCAR file not found.")
        return False

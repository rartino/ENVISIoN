#
#  ENVISIoN
#
#  Copyright (c) 2017-2018 Anders Rehult, Marian Brännvall, Andreas Kempe, Viktor Bernholtz
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
import numpy as np
from ..h5writer import _write_fermisurface

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *){4}')

# Class representing a point in K-space.
# Contains its coordinates in three dimensions
# as well as a list of energies associated with
# the point.
class KPoint:
    def __init__(self):
        self.coordinates = list()
        self.energies = list()

def fermi_parse(vasp_dir):
    """
    Parses band structure data from EIGENVAL and Fermi energy from DOSCAR

    Parameters
    ----------
   vasp_dir : string
       string containing path to VASP-files

    Returns
    -------

    kval_list : list
        list containing all the K-points
    fermi_energy: float
        float containing the Fermi energy
    reciprocal_lattice_vectors: list 
        list containing vectors with 3 floats

    """
    data = None
    kval = None
    kval_list = []
    energy_count = 0
    i = 0

    eigenval_file = os.path.join(vasp_dir, 'EIGENVAL')
    try:
        with open(eigenval_file, "r") as f:
            for line in f:
                match_float = line_reg_float.match(line)
                match_int = line_reg_int.match(line)
                if match_int:
                     data = [int(v) for v in line.split()]
                     energy_count = int(data[2])
                if data and match_float:
                     kval = KPoint()
                     for u in range(3):
                        kval.coordinates.append(float(line.split()[u]))
                elif kval and data:
                      kval.energies.append(float(line.split()[1]))
                      i += 1
                if i == energy_count and kval:
                       kval_list.append(kval)
                       kval = None
                       i = 0
    except OSError:
        print('EIGENVAL file not in directory. Skipping.')
        return [], 0

    # Parses fermi energy from DOSCAR
    doscar_file = os.path.join(vasp_dir, 'DOSCAR')
    try:
        with open(doscar_file, "r") as f:
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            line = next(f)
            fermi_energy = float(line.split()[3])

    except OSError:
        print('DOSCAR file not in directory. Skipping.')
        return [], 0

    # Parses reciprocal lattice vectors from OUTCAR
    outcar_file = os.path.join(vasp_dir, 'OUTCAR')
    try:
        with open(outcar_file, 'r') as f:
            while not "reciprocal lattice vectors" in  next(f):
                pass

            vectors_as_strings = []
            for i in range(0, 3):
                vectors_as_strings.append(re.sub(' +', ' ', next(f).strip()))
            
            reciprocal_lattice_vectors = []

            for i in range(0, 3):
                vectors = vectors_as_strings[i].split(' ')
                reciprocal_lattice_vectors.append([vectors[3],
                                                   vectors[4],
                                                   vectors[5]])
    except OSError:
        print('OUTCAR file not in directory. Skipping.')
        return [], 0
    
    return kval_list, fermi_energy, reciprocal_lattice_vectors

def fermi_surface(h5file, vasp_dir):
    """
    Parses band structure data from EIGENVAL

    Parameters
    ----------
    h5file : str
        String that asserts which HDF-file to write to
    vasp_dir : str
        Path to directory containing EIGENVAL file

    Returns
    -------
    bool
        Return True if EIGENVAL was parsed, False otherwise

    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if '/FermiSurface' in h5:
                print('Fermi surface data already parsed. Skipping.')
                return False

    kval_list, fermi_energy, reciprocal_lattice_vectors = fermi_parse(vasp_dir)
    if not kval_list:
        print('Something went wrong when parsing Fermi surface data in folder {}'.format(vasp_dir))
        return False

    _write_fermisurface(h5file, kval_list, fermi_energy, reciprocal_lattice_vectors)
    print('Fermi surface data was parsed successfully.')
    return True

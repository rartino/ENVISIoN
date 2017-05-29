#
#  ENVISIoN
#
#  Copyright (c) 2017 Fredrik Segerhammar
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
import h5py
import numpy as np
from ..h5writer import _write_dos
from .incar import *

def dos_line(f, ndos):
    """
        Parses density of states data from DOSCAR

        Parameters
        ----------
        f : file object
	    File object containing data in DOSCAR file
        ndos: int
		Number of lines in f to be parsed
		
        Returns
        -------
        data : list
		List of density of states data
        line_length : float
		Amount of column in each line

    """
    data = []
    line_length = []
    for n in range(ndos):
        line = next(f)
        if not line_length:
            line_length = len(line.split())
        if len(data) != len(line.split()):
            data = [[] for i in range(len(line.split()))]
        for i, element in enumerate(line.split()):
            data[i].append(float(element))
    return data, line_length

def parse_doscar(h5file,vasp_file):
    """
	Parses density of states data from DOSCAR

    Parameters
    ----------
    h5file : str
	String containing path to HDF-file
    vasp_file : str
	String containing path to DOSCAR file
		
    Returns
    -------
    total : list
        List of names for total datasets
    partial : list
	List of names for partial datasets
    total_data : list
	List containing all the data for total density of states
    partial_list : list
	List containing all the data for partial density of states
    fermi_energy : float

    """
    total = []
    partial = []
    
    # Parse file.
    with open(vasp_file, "r") as f:

        line = next(f)
        line = next(f)
        ediff = next(f)
        coord = next(f)
        system = next(f)
        line = next(f)
        header = {"Highest energy": float(line.split()[0]), "Lowest energy": float(line.split()[1]), "ndos": int(line.split()[2]), "Fermi energy": float(line.split()[3]), "weight": float(line.split()[4])}

        if os.path.isfile(h5file):
            with h5py.File(h5file,'r') as h5:
                if '/incar' in h5:
                    incar = h5.get('/incar')
                    if np.array(incar.get('LORBIT')) == '10':
                        if np.array(incar.get('ISPIN')) == '1':
                            total = ["Energy", "DOS", "Integrated DOS"]
                            partial = ["Energy", "s-DOS", "p-DOS", "d-DOS", "f-DOS"]
                        if np.array(incar.get('ISPIN')) == '2':
                            total = ["Energy", "DOS(up)", "DOS(dwn)", "Integrated DOS(up)", "Integrated DOS(dwn)"]
                            partial = ["Energy", "s-DOS(up)", "s-DOS(dwn)", "p-DOS(up)", "p-DOS(dwn)", "d-DOS(up)", "d-DOS(dwn)", "f-DOS(up)", "f-DOS(dwn)"]
                    if np.array(incar.get('LORBIT')) == '11':
                        total = ["Energy", "DOS", "Integrated DOS"]
                        partial = ["Energy", "s-DOS", "p-DOS(x)", "p-DOS(y)", "p-DOS(z)", "d-DOS(xy)", "d-DOS(yz)", "d-DOS(z2)", "d-DOS(xz)", "d-DOS(x2y2)", "f-DOS(-3)", "f-DOS(-2)", "f-DOS(-1)", "f-DOS(0)", "f-DOS(1)", "f-DOS(2)", "f-DOS(3)"]

        total_data, line_length = dos_line(f, header["ndos"])
        if not total:
            print("Because INCAR data was not written to the hdf5 file the data of the DOS cannot be specified.")
            total = ['Energy']
            for _ in range(line_length - 1):
                total.append('Unknown DOS {}'.format(_))
        partial_list = []
        for line in f:
            partial_data, line_length = dos_line(f, header["ndos"])
            partial_list.append(partial_data)
        if not partial:
            partial = ['Energy']
            for _ in range(line_length - 1):
                partial.append('Unknown DOS {}'.format(_))
    return total, partial, total_data, partial_list, header["Fermi energy"]

def dos(h5file, vasp_dir):
    """
	Parses density of states data from DOSCAR

    Parameters
    ----------
	h5file : str
		String containing path to HDF-file
	vasp_dir : str
		String containing path to directory DOSCAR is in

    Returns
    -------
    bool
		Return True if DOSCAR was parsed, False otherwise

    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if '/FermiEnergy' and 'DOS/Total' and 'DOS/Partial' in h5:
                print('Density of states data already parsed. Skipping.')
                return False

    incar(h5file, vasp_dir)
    try:
        vasp_file = os.path.join(vasp_dir, 'DOSCAR')
        total, partial, total_data, partial_list, fermi_energy = parse_doscar(h5file, vasp_file)
    except FileNotFoundError:
        print('DOSCAR file not in directory. Skipping.')
        return False
    _write_dos(h5file, total, partial, total_data, partial_list, fermi_energy)
    print('Density of states data was parsed successfully.')
    return True
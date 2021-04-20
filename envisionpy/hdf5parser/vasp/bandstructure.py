#
#  ENVISIoN
#
#  Copyright (c) 2017 Fredrik Segerhammar, Anton Hjert and Abdullatif Ismail
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
#  Alterations to this file by Daniel Thomas
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
import h5py
from h5writer import _write_bandstruct
from fermiEnergy import fermi_energy_parser
from unitcell import _find_line, coordinates_re
from check_for_parse import has_been_parsed

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *){4}')

def _parse_lattype(vasp_dir):
    """Retrieves lattice type from OUTCAR file.
    Parameters
    ----------
    vasp_dir : string
        string containing path to VASP-files

    Returns
    -------
    found_lattype : string
        string of lattice type
    """
    outcar_file = os.path.join(vasp_dir, 'OUTCAR')
    try:
        with open(outcar_file, "r") as f:
            lattype_re = re.compile(r'(?<=Found a ).*?(?= cell.)')
            match = False
            found_lattype = []
            for line in f:
                match = lattype_re.search(line)
                if match:
                    found_lattype = match.group()
    except StopIteration:
        pass # if EOF is reached here
    except OSError:
        print('OUTCAR file not in directory.')
        return []
    return found_lattype

def _parse_kpoints(vasp_dir):
    """Retrives coordinates from KPOINTS file
    and removes duplicates.

    Parameters
    ----------
    vasp_dir : string
        string containing path to VASP-files

    Returns
    -------
    cleaned_coords : list of float
        List of parsed coordinates
    """

    match = False
    kpoints_file = os.path.join(vasp_dir, 'KPOINTS')
    try:
        with open(kpoints_file, "r") as f:
            found_coords = []
            match = _find_line(coordinates_re, f)
            while match:
                coords = [float(coordinate) for coordinate in match.groups()]
                found_coords.append(coords)
                match = coordinates_re.search(next(f))
                if not match:
                    match = coordinates_re.search(next(f))
    except StopIteration:
        pass # if EOF is reached here
    except OSError:
        print('KPOINTS file not in directory.')
        return []
    sorted_coords = sorted(found_coords)
    cleaned_coords = [sorted_coords[i] for i in range(len(sorted_coords)) if i == 0 or sorted_coords[i] != sorted_coords[i-1]]

    return cleaned_coords

def _symmetry_retriever(vasp_dir):
    """Compares input from OUTCAR and KPOINTS with stored
    coordinates and symbols to find a match. Retrieves the
    matched combination. The symmetry_points and
    symmetry_symbols variables contains high symmetry data
    in the following order:
    [CUB, BCC, FCC, TET, HEX, ORC, TRI1a/TRI2a, TRI1b/TRI2b]

    Parameters
    ----------
    vasp_dir : str
        Path to directory containing vasp files

    Returns:
    --------
    result_points: list of float
        list of matched symmetry coordinates
    result_symbs: list of characters
        list of matched symmetry symbols
    """

    symmetry_points = [[[0.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0.5, 0.5], [0.0, 0.5, 0.0]],
                       [[0.0, 0.0, 0.0], [0.5, -0.5, 0.5], [0.25, 0.25, 0.25], [0.0, 0.0, 0.5]],
                       [[0.0, 0.0, 0.0], [0.375, 0.375, 0.75], [0.5, 0.5, 0.5], [0.625, 0.25, 0.625], [0.5, 0.25, 0.75], [0.5, 0.0, 0.5]],
                       [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.0, 0.5, 0.0], [0.0, 0.0, 0.5]],
                       [[0.0, 0.0, 0.0], [0.0, 0.0, 0.5], [0.33333, 0.33333, 0.5], [0.33333, 0.33333, 0.0], [0.5, 0.0, 0.5], [0.5, 0.0, 0.0]],
                       [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.5]],
                       [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.5], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.5]],
                       [[0.0, 0.0, 0.0], [0.5, -0.5, 0.0], [0.0, 0.0, 0.5], [-0.5, -0.5, 0.5], [0.0, -0.5, 0.5], [0.0, -0.5, 0.0], [0.5, 0.0, 0.0], [-0.5, 0.0, 0.5]]]

    symmetry_symbols = [['\u0393', 'M', 'R', 'X'], ['\u0393', 'H', 'P', 'N'], ['\u0393', 'K', 'L', 'U', 'W', 'X'],
                        ['\u0393', 'A', 'M', 'R', 'X', 'Z'], ['\u0393', 'A', 'H', 'K', 'L', 'M'],
                        ['\u0393', 'R', 'S', 'T', 'U', 'X', 'Y', 'Z'],
                        ['\u0393', 'L', 'M', 'N', 'R', 'X', 'Y', 'Z'],
                        ['\u0393', 'L', 'M', 'N', 'R', 'X', 'Y', 'Z']]

    found_points = _parse_kpoints(vasp_dir)
    found_lattype = _parse_lattype(vasp_dir)
    result_points = []
    result_symb = []
    for i in range(len(symmetry_points)):
        if len(found_points) == 8:
            if found_lattype == 'simple orthorhombic':
                result_points = symmetry_points[5]
                result_symb = symmetry_symbols[5]
                return result_points, result_symb
            if found_lattype == 'triclinic':
                if sorted(symmetry_points[6]) == sorted(found_points):
                    result_points = symmetry_points[6]
                    result_symb = symmetry_symbols[6]
                    return result_points, result_symb
                if sorted(symmetry_points[7]) == sorted(found_points):
                    result_points = symmetry_points[7]
                    result_symb = symmetry_symbols[7]
                    return result_points, result_symb
        if len(symmetry_points[i]) == len(found_points) and len(found_points) != 8:
            if sorted(symmetry_points[i]) == sorted(found_points):
                result_points = symmetry_points[i]
                result_symb = symmetry_symbols[i]
                return result_points, result_symb
    return result_points, result_symb

def bandstruct_parse(file_object):
    """
    Parses band structure data from EIGENVAL

    Parameters
    ----------
    file_object : file object
            File object containing data in EIGENVAL

    Returns
    -------
    band_data : list
            list containing all the band data
    kval_list : list
            list containing all the K-points

    """
    data = None
    kval = None
    kval_list = []
    band_data = []
    i = 0

    for line in file_object:
        match_float = line_reg_float.match(line)
        match_int = line_reg_int.match(line)
        if match_int:
            data = [int(v) for v in line.split()]
            band_data = [[] for _ in range(data[2])]
        if data and match_float:
            kval = []
            for u in range(3):
                kval.append(float(line.split()[u]))
        elif kval and data:
            band_data[i].append(float(line.split()[1]))
            i += 1
        if i == len(band_data) and kval:
            kval_list.append(kval)
            kval = None
            i = 0
    return band_data, kval_list


def bandstructure(h5file, vasp_dir):
    """
    Parses band structure data from EIGENVAL and
    high symmetry data from OUTCAR and KPOINTS

    Parameters
    ----------
    h5file : str
        String that asserts which HDF-file to write to
    vasp_dir : str
        Path to directory containing EIGENVAL file

    Returns
    -------
    bool
        Return True if KPOINTS and
        EIGENVAL and OUTCAR was parsed,
        False otherwise

    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if '/Bandstructure' and '/Highcoordinates' in h5:
                print('Band structure data already parsed. Skipping.')
                return False
    try:
        with open(os.path.join(vasp_dir, 'EIGENVAL'), 'r') as f:
            band_data, kval_list = bandstruct_parse(f)
            # Get's the Fermi energy as an int if the DOSCAR file exist.
            fermi_energy = fermi_energy_parser(vasp_dir)
            for band in band_data:
                for data in band:
                    data -= fermi_energy
        if not band_data:
            print('EIGENVAL does not contain any data for band structure. Skipping.')
            return False
    except OSError:
        print('EIGENVAL file not in directory. Skipping.')
        return False

    parsed_coords, parsed_symbols = _symmetry_retriever(vasp_dir)
    if parsed_coords:
        _write_bandstruct(h5file, band_data, kval_list, parsed_symbols, parsed_coords)
        print('Band structure data was parsed successfully.')
        return True
    elif not parsed_coords and os.path.isfile(os.path.join(vasp_dir, 'KPOINTS')) and os.path.isfile(os.path.join(vasp_dir, 'OUTCAR')):
        print('Cannot interpret data in KPOINTS or OUTCAR')
        return False
    else:
        return False

#
#  ENVISIoN
#
#  Copyright (c) 2019 Abdullatif Ismail
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
#  Alterations to this file by Anton Hjert
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
import os, sys, h5py, inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/../'))
from h5writer import _write_fermi_energy


def fermi_energy_parser(vasp_dir):
    """
    Parses fermi energy from DOSCAR file.
    :param vasp_dir: string containing path to VASP-file.
    :return: float containing fermi energy.
    """
    # Open DOSCAR file.
    outcar_file = vasp_dir + '/DOSCAR'
    try:
        with open(outcar_file, "r") as f:
            (next(f))
            next(f)
            next(f)
            next(f)
            next(f)
            line = next(f)
            fermi_energy = float(line.split()[3])
    except OSError:
        print('DOSCAR file not in directory. Skipping.')
        return 0
    except StopIteration:
        print('Data not found in DOSCAR. Skipping.')
        return 0
    return fermi_energy


def fermi_energy(h5file, vasp_dir):
    """
    Parses fermi energy from DOSCAR file.
    :param h5file: String with path to HDF5 file.
    :param vasp_dir: String with path to VASP directory.
    :return: bool, True if DOSCAR file was parsed, False otherwise.
    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'a') as h5:
            if '/FermiEnergy' in h5:
                print('Fermi energy already parsed. Skipping.')
                return False
    energy = fermi_energy_parser(vasp_dir)
    if _write_fermi_energy(h5file, energy) == 0:
        return False
    else:
        print('Fermi energy was parsed successfully.')
        return True

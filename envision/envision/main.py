#
#  ENVISIoN
#
#  Copyright (c) 2017 Denise Härnström
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
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
import os,sys
import h5py
import inspect
path_to_current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_dir+'/parser/vasp'))
from bandstructure import bandstructure
from doscar import dos
from md import md
from unitcell import unitcell
from volume import charge, elf
from fermi import fermi_surface
from PKF import paircorrelation

def parse_all(h5_path, dir):
    """parse_all
    Parse everything in given directory. All parsers are called upon. Writes message on what 
    is being parsed and if the parsing succeded or not. Returns a list of names of 
    groups in the HDF5-file if it exists after parsing, None otherwise.
    
    Parameters
    ----------
    h5_path : str
        Path to HDF5 file
        
    dir : str
        Path to directory containing files to be parsed
        
    Returns
    -------
        List of names of groups in HDF5-file if it exists, None otherwise
    """
    func_dict = {
        'unitcell from VASP': unitcell,
        'molecular dynamics from VASP': md,
        'charge from VASP': charge,
        'ELF from VASP': elf,
        'DOS from VASP': dos,
        'bandstructure from VASP': bandstructure
        ,'fermi surface from VASP': fermi_surface,
        'PCF from VASP': paircorrelation
    }
    parsed_list = []
    for key, function in func_dict.items():
        print("Parsing "+key)
        if function(h5_path, dir):
            parsed_list.append(key)
            print("Parsed")
        else:
            print("Nothing parsed")

    if os.path.isfile(h5_path):
        with h5py.File(h5_path, 'r') as h5:
            #keys = list(h5.keys())
            return parsed_list
    else:
        return None

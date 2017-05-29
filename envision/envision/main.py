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

import os
import h5py
from . import parser

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
        'unitcell from VASP': parser.vasp.unitcell,
        'molecular dynamics from VASP': parser.vasp.md,
        'charge from VASP': parser.vasp.charge,
        'ELF from VASP': parser.vasp.elf,
        'DOS from VASP': parser.vasp.dos,
        'bandstructure from VASP': parser.vasp.bandstructure
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
            keys = list(h5.keys())
            return keys
    else:
        return None

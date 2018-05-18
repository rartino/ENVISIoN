#
#  ENVISIoN
#
#  Copyright (c) 2017-2018 Robert Cranston, Marian Brännvall
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

from itertools import *
from functools import *
import os
import h5py
import regex
from .log import *
from .util import *
from ..h5writer import _write_incar

def parse_incar(h5file, vasp_file):
    """
	Parses set values from INCAR

    Parameters
    ----------
	h5file : str
		String containing path to HDF-file
	vasp_file : str
		String containing path to INCAR file
		
    Returns
    -------
    incar_data : dict
		Dictionary containing all the data in INCAR
    """

    # This should be done more globally.
    LOG_LEVEL_PRINT = LOG_WARNING
    
    # Define validation data.
    valid_keys = [
            "NGX",
            "NGY",
            "NGZ",
            "NGXF",
            "NGYF",
            "NGZF",
            "NBANDS",
            "NBLK",
            "SYSTEM",
            "NWRITE",
            "ISTART",
            "ICHARG",
            "ISPIN",
            "MAGMOM",
            "INIWAV",
            "ENCUT",
            "PREC",
            "PREC",
            "NELM",
            "NELMINandNELMDL",
            "EDIFF",
            "EDIFFG",
            "NSW",
            "NBLOCKandKBLOCK",
            "IBRION",
            "ISIF",
            "IWAVPR",
            "ISYM",
            "SYMPREC",
            "LCORR",
            "POTIM",
            "TEBEG",
            "TEEND",
            "SMASS",
            "NPACOandAPACO",
            "POMASS",
            "ZVAL",
            "RWIGS",
            "NELECT",
            "NUPDOWN",
            "EMIN",
            "EMAX",
            "ISMEAR",
            "SIGMA",
            "ALGO",
            "IALGO",
            "LREAL",
            "ROPT",
            "GGA",
            "VOSKOWN",
            "DIPOL",
            "AMIX",
            "BMIX",
            "WEIMIN",
            "EBREAK",
            "DEPER",
            "TIME",
            "LWAVE",
            "LCHARG",
            "LVTOT",
            "LVHAR",
            "LELF",
            "LORBIT",
            "NPAR",
            "LSCALAPACK",
            "LSCALU",
            "LASYNC",
        ]

    # Defines regexes.
    key_regstr = r' *(?<key>[_a-zA-Z][_a-zA-Z0-9]*) *'
    value_regstr = r' *(?<value>[^ ;]+) *'
    keyvalue_regstr = r'(?:' + key_regstr + r'=' + value_regstr + r')*'
    keyvaluelist_regstr = keyvalue_regstr + r'(?:' + r';' + keyvalue_regstr + r')*'
    comment_regstr = r'(?<comment>.*)'
    line_regstr = r'^' + keyvaluelist_regstr + comment_regstr + r'$'
    line_reg = regex.compile(line_regstr)
    incar_data = {}
    
    # Parses file.
    with open(vasp_file, "r") as f:

        file_lines = vasp_file_lines(f, line_continuation=True)
        for line_nr, line in file_lines:

            match = line_reg.match(line)
            if not match:
                log(LOG_ERROR, vasp_file, line_nr, "Unsupported format", line)

            capturesdict = match.capturesdict()
            for key, value in zip(capturesdict['key'], capturesdict['value']):
                if key not in valid_keys:
                    log(LOG_WARNING, vasp_file, line_nr, "Unrecognized key", key)
                incar_data[key] = value
    return incar_data

def incar(h5file, vasp_dir):
    """
	Parses set values from INCAR and writes to HDF5 file

    Parameters
    ----------
	h5file : str
		String containing path to HDF-file
	vasp_dir : str
		Path to directory containing INCAR file
		
    Returns
    -------
	bool
		Return True if INCAR was parsed, False otherwise
    """
    if os.path.isfile(h5file):
        with h5py.File(h5file, 'r') as h5:
            if '/incar' in h5:
                print('INCAR data already parsed. Skipping.')
                return False
    vasp_file = os.path.join(vasp_dir, 'INCAR')
    try:
        incar_data = parse_incar(h5file, vasp_file)
    except FileNotFoundError:
        print('INCAR file not in directory. Skipping.')
        return False
    _write_incar(h5file, incar_data)
    print('INCAR data was parsed successfully.')
    return True

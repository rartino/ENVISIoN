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
import re
import h5py
import numpy as np
from .unitcell import _parse_lattice, _find_elements, _parse_coordinates, _cartesian
from ..h5writer import _write_basis, _write_md, _write_steps

def md(h5_path, vasp_dir, elements=None):
    if os.path.isfile(h5_path):
        with h5py.File(h5_path, 'r') as h5:
            if "/MD" in h5:
                print("Already parsed. Skipping.")
                return False

    try:
        with open(os.path.join(vasp_dir,'XDATCAR'), "r") as f:
            scaling_factor, basis = _parse_lattice(f)
            elements, atoms = _find_elements(f, elements, vasp_dir)
            _write_basis(h5_path, scaling_factor * basis)

            step = 0
            while True:
                coords_list = []
                try:
                    coords_list = _parse_coordinates(f,sum(atoms))
                except Exception as instance:
                    text, length = instance.args
                    if length != 0:
                    	raise
                if not coords_list:
                    break
                _write_md(
                    h5_path,
                    atoms,
                    coords_list,
                    elements,
                    step
                )
                step += 1
            _write_steps(h5_path, step)
            return True
    except FileNotFoundError:
        print("XDATCAR file not found.")
        return False

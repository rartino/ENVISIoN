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
from .unitcell import _parse_lattice, _find_elements, _parse_coordinates
from ..h5writer import _write_basis, _write_md, _write_steps

def md(h5_path, vasp_dir, elements=None):
    if os.path.isfile(h5_path):
        with h5py.File(h5_path, 'r') as h5:
            if "/MD" in h5:
                print("Already parsed. Skipping.")
                return False

    try:
        with open(os.path.join(vasp_dir,'XDATCAR'), "r") as f:
            pdata = _parse_lattice(f)
            elements = _find_elements(
                    elements,
                    pdata['elements'],
                    vasp_dir,
                    len(pdata['atom_count'])
            )
            _write_basis(
                h5_path,
                pdata['scaling_factor']*np.asarray(pdata['basis'])
            )

            step = 0
            while True:
                coords_list = _parse_coordinates(
                    f,
                    sum(pdata['atom_count']),
                    pdata['cartesian'],
                    np.linalg.inv(
                        pdata['scaling_factor']*np.asarray(pdata['basis'])
                    )
                )
                if not coords_list:
                    break
                _write_md(
                    h5_path,
                    pdata['atom_count'],
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

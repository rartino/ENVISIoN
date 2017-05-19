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

import re
import h5py
import numpy as np
from ..h5writer import _write_bandstruct

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *){4}')


def bandstruct_parse(eigen_file):
    data = None
    kval = None
    kval_list = []
    eigenval = []
    i = 0
    with open(eigen_file, 'r') as f:
        for line in f:

            match_float = line_reg_float.match(line)
            match_int = line_reg_int.match(line)

            if match_int:
                data = [int(v) for v in line.split()]
                eigenval = [[] for _ in range(data[2])]
            if data and match_float:
                kval = []
                for u in range(3):
                    kval.append(float(line.split()[u]))
            elif kval and data:
                eigenval[i].append(float(line.split()[1]))
                i += 1
            if i == len(eigenval) and kval:
                kval_list.append(kval)
                kval = None
                i = 0
        return eigenval, kval_list, data


def bandstructure(eigen_file, h5_path):
    try:
        eigenval, kval_list, data = bandstruct_parse(eigen_file)
    except FileNotFoundError:
        print("EIGENVAL file not found.")
        return
    try:
        _write_bandstruct(h5_path, eigenval, kval_list)
    except Exception:
        print("Bandstructure dataset already exists.")
        return

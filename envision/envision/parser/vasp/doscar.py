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

import h5py
import numpy as np
from ..h5writer import _write_dos

def dos_line(f, ndos, line):
    data = []
    for n in range(ndos):
        line = next(f)
        if len(data) != len(line.split()):
            data = [[] for i in range(len(line.split()))]
        i = 0
        for element in line.split():
            data[i].append(float(element))
            i+=1
    return data, line

def parse_doscar(doscar_file, h5file):
    """
    TODO
    """

    # Parse file.
    with open(doscar_file, "r") as f:

        line = next(f)
        line = next(f)
        ediff = next(f)
        coord = next(f)
        system = next(f)
        line = next(f)
        header = {"Highest energy": float(line.split()[0]), "Lowest energy": float(line.split()[1]), "ndos": int(line.split()[2]), "Fermi energy": float(line.split()[3]), "weight": float(line.split()[4])}

        with h5py.File(h5file,'r') as h:

            # sektionen 'indata_specific/vasp/incar' Beror egentligen på utseendet i h5-filen
            incar = h.get('indata_specific/vasp/incar')


            if np.array(incar.get('LORBIT')) == '10':
                if np.array(incar.get('ISPIN')) == '1':
                    total = ["energy", "DOS", "Integrated DOS"]
                    partial = ["energy", "s-DOS", "p-DOS", "d-DOS", "f-DOS"]
                if np.array(incar.get('ISPIN')) == '2':
                    total = ["energy", "DOS(up)", "DOS(dwn)", "integrated DOS(up)", "integrated DOS(dwn)"]
                    partial = ["energy", "s-DOS(up)", "s-DOS(dwn)", "p-DOS(up)", "p-DOS(dwn)", "d-DOS(up)", "d-DOS(dwn)", "f-DOS(up)", "f-DOS(dwn)"]

        total_data, line = dos_line(f, header["ndos"], line)
        partial_list = []
        for line in f:
            partial_data, line = dos_line(f, header["ndos"], line)
            partial_list.append(partial_data)

    return total, partial, total_data, partial_list, header["Fermi energy"]

def doscar(h5file, doscar_file, incarh5):
    try:
        total, partial, total_data, partial_list, fermi_energy = parse_doscar(doscar_file,incarh5)
    except FileNotFoundError:
        print("DOSCAR file not found.")
        return
    except Exception:
        print("DOSCAR Parsing failed because there is no INCAR.")
        return
    try:
        _write_dos(h5file, total, partial, total_data, partial_list, fermi_energy)
    except Exception:
        print("DOS dataset already exists.")
        return

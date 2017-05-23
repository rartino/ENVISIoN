import os
import h5py
from . import parser

def parse_all(h5_path, dir):
    func_dict = {
        'unitcell from VASP': parser.vasp.unitcell,
        'molecular dynamics from VASP': parser.vasp.md,
        'charge from VASP': parser.vasp.charge,
        'ELF from VASP': parser.vasp.elf,
        'DOS from VASP': parser.vasp.doscar,
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

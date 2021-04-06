import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import h5py
#from h5writer import _write_basis, _write_scaling_factor, _write_coordinates, _write_forces
from pathlib import Path
# Define coordinates regex.
coordinates_re = re.compile(r' +'.join([r'([+-]?[0-9]+\.[0-9]+)'] * 3))


def mol_dynamic_parser(hdf_file_path, vasp_dir_path):
    outcar_file_path = Path(vasp_dir_path).joinpath('OUTCAR')
    xdatcar_file_path = Path(vasp_dir_path).joinpath('XDATCAR')
    md_ok = False
    print(md_ok)

    if not outcar_file_path.exists() or not xdatcar_file_path.exists():
        raise FileNotFoundError('Cannot find one of the two vasp files in directory')

    with outcar_file_path.open('r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            if 'IBRION' in line:
                line_list = list(line.split(" "))
                new_line_list = []
                for x in range(len(line_list)):
                    if line_list[x] != "":
                        new_line_list.append(line_list[x])
                line_list = new_line_list
                if line_list[2] == "0":
                    md_ok = True
    print(md_ok)



mol_dynamic_parser("test.hdf5","Cu_band_CUB/")

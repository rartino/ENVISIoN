import os
import sys
import itertools
import h5py
import numpy as np

# make module available
#PATH_TO_HDF5 = os.path.expanduser("~/ENVISIoN/HDF5/demo.hdf5")
#PATH_TO_VASP_CALC = os.path.expanduser("~/ENVISIoN/data")
PATH_TO_parser = os.path.expanduser("~/ENVISIoN/envision/envision/parser")
sys.path.append(os.path.abspath(PATH_TO_parser))

import h5writer


def _parse_pcdat(h5file, vasp_file):
#   The function parse PCDAT and is called upon by paircorrelation(h5file, vasp_dir)

#    Parameters
#    __________
#    h5file: str
#        String containing path to HDF5-file.

#    vasp_file: str
#        Is the path to vasp-file PCDAT.

#    Return
#    ______
#    A list of values, the average number of atoms type n given equally spaced distances from an average atom of type n.

#    Läs hur många atomslag som finns
    with open(vasp_file, "r") as vasp_fileobj:
        line = next(vasp_fileobj)
        print(line)


# The function script from inviwo will call with envision.parser.vasp.paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)

def paircorrelation(h5file, vasp_dir):
#   The function which script from inviwo will call with the command:  envision.parser.vasp.paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)

#    Parameters
#    __________
#    h5file: str
#        String containing path to HDF5-file.

#    vasp_dir:
#        Is a path to the directory where VASP-files are.

#    Return
#    ______
#    Bool: True if parsed, False otherwise.

    vasp_file = os.path.join(vasp_dir, "PCDAT")
    _parse_pcdat(h5file, vasp_file)

#paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)

# Preparements for testing

# Path to the ENVISIoN directory
PATH_TO_ENVISION = "C:/Users/Daniel/ENVISIoN/ENVISIoN"

import os, sys, h5py
sys.path.append(PATH_TO_ENVISION)
import envisionpy.hdf5parser
import pytest

########################################################################################
# First test of a VASP-directory which is compatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC = "C:/Users/Daniel/Downloads/bandstrukturer_test/Cu_band_CUB"

# Path to the resulting hdf5 file 
PATH_TO_HDF5 = "C:/Users/Daniel/Downloads/HDF5-TESTS/band_demo.hdf5"

# Parse
envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5, PATH_TO_VASP_CALC)
envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5, PATH_TO_VASP_CALC)

# Test if the generated HDF5-file contains correct information

def test_parse_1():
    if os.path.isfile(PATH_TO_HDF5):
            with h5py.File(PATH_TO_HDF5, 'r') as h5:
                assert '/Bandstructure' and '/BandStructure' and '/FermiEnergy' and '/Highcoordinates' in h5

########################################################################################
# Second test of a VASP-directory which is incompatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC_1 = "C:/Users/Daniel/Downloads/bandstrukturer_test/CuFeS2_band_CBT2"

# Path to the resulting hdf5 file 
PATH_TO_HDF5_1 = "C:/Users/Daniel/Downloads/HDF5-TESTS/band_demo1.hdf5"

# Parse
envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)
envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)

# Test if the generated HDF5-file contains incorrect information

def test_parse_2():
    if os.path.isfile(PATH_TO_HDF5_1):
            with h5py.File(PATH_TO_HDF5_1, 'r') as h5:
                assert '/Bandstructure' and '/BandStructure' and '/FermiEnergy' and '/Highcoordinates' not in h5

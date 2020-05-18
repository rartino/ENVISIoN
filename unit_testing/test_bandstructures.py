# Preparements for testing

# Path to the ENVISIoN directory

import os, sys, h5py
import pytest

# path to current directory
TEST_DIR = os.path.dirname(os.path.realpath(__file__))

# check if INVIWO_HOME is set if not assume this unit test is one directory below envision root
sys.path.append(os.environ.get('INVIWO_HOME', os.path.join(TEST_DIR, os.pardir)))
import envisionpy.hdf5parser

########################################################################################
# First test of a VASP-directory which is compatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC = os.path.join(TEST_DIR, "resources/Cu_band_CUB")

# Path to the resulting hdf5 file
PATH_TO_HDF5 = os.path.join(TEST_DIR, "band_demo.hdf5")

# Parse
envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5, PATH_TO_VASP_CALC)
envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5, PATH_TO_VASP_CALC)

# Test if the generated HDF5-file contains correct information

def test_parse_1():
    if os.path.isfile(PATH_TO_HDF5):
            with h5py.File(PATH_TO_HDF5, 'r') as h5:
                assert '/Bandstructure' in h5
                assert '/BandStructure' in h5
                assert '/FermiEnergy' in h5
                assert '/Highcoordinates' in h5

########################################################################################
# Second test of a VASP-directory which is incompatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC_1 = os.path.join(TEST_DIR, "resources/CuFeS2_band_CBT2")

# Path to the resulting hdf5 file
PATH_TO_HDF5_1 = os.path.join(TEST_DIR, "band_demo1.hdf5")

# Parse
envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)
envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)

# Test if the generated HDF5-file contains incorrect information

def test_parse_2():
    if os.path.isfile(PATH_TO_HDF5_1):
            with h5py.File(PATH_TO_HDF5_1, 'r') as h5:
                assert '/Bandstructure'  not in h5
                assert '/BandStructure' not in h5
                assert '/FermiEnergy' in h5
                assert '/Highcoordinates' not in h5


# cleanup
os.remove(PATH_TO_HDF5)
os.remove(PATH_TO_HDF5_1)

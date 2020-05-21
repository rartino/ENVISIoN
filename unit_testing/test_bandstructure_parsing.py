#
#  ENVISIoN
#
#  Copyright (c) 2017-2019 Daniel Thomas
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
##############################################################################################

# Preparements for testing

import os, sys, h5py
import pytest

# path to current directory
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(TEST_DIR, os.pardir))
import envisionpy.hdf5parser

########################################################################################
# First test of a VASP-directory which is compatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC = os.path.join(TEST_DIR, "resources/Cu_band_CUB")

# Path to the resulting hdf5 file
PATH_TO_HDF5 = os.path.join(TEST_DIR, "band_demo.hdf5")

def test_parse_first():
    """Testing if correct bandstructure parsing of a compatible VASP-directory.
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    # Parse
    envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5, PATH_TO_VASP_CALC)
    envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5, PATH_TO_VASP_CALC)

    # Test if the generated HDF5-file contains correct information

    if os.path.isfile(PATH_TO_HDF5):
            with h5py.File(PATH_TO_HDF5, 'r') as h5:
                assert '/Bandstructure' in h5
                assert '/BandStructure' in h5
                assert '/FermiEnergy' in h5
                assert '/Highcoordinates' in h5
    # cleanup
    os.remove(PATH_TO_HDF5)

########################################################################################
# Second test of a VASP-directory which is incompatible with the bandstructure parser.

# Path to the vasp directory
PATH_TO_VASP_CALC_1 = os.path.join(TEST_DIR, "resources/CuFeS2_band_CBT2")

# Path to the resulting hdf5 file
PATH_TO_HDF5_1 = os.path.join(TEST_DIR, "band_demo1.hdf5")

def test_parse_second():
    """Testing if correct bandstructure parsing of a incompatible VASP-directory.
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    # Parse
    envisionpy.hdf5parser.bandstructure(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)
    envisionpy.hdf5parser.fermi_energy(PATH_TO_HDF5_1, PATH_TO_VASP_CALC_1)

    # Test if the generated HDF5-file contains incorrect information

    if os.path.isfile(PATH_TO_HDF5_1):
            with h5py.File(PATH_TO_HDF5_1, 'r') as h5:
                assert '/Bandstructure'  not in h5
                assert '/BandStructure' not in h5
                assert '/FermiEnergy' in h5
                assert '/Highcoordinates' not in h5
    # cleanup
    os.remove(PATH_TO_HDF5_1)

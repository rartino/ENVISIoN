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
import os, sys
import pytest
import h5py

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(TEST_DIR, os.pardir))


from envisionpy.hdf5parser import fermi_parser


@pytest.fixture(scope='function')
def h5file():
    # setup
    path_to_vasp_calc = os.path.join(TEST_DIR, "resources/FCC-Cu")
    path_to_hdf5 = os.path.join(TEST_DIR, "tmp.hdf5")

    fermi_parser(path_to_hdf5, path_to_vasp_calc)
    # run tests
    yield path_to_hdf5

    # cleanup
    os.remove(path_to_hdf5)


def test_fermi_parsing(h5file):
    assert os.path.isfile(h5file)

    with h5py.File(h5file, 'r') as h5:
        assert 'bands' in h5
        assert 'fermi_energy' in h5
        assert 'basis' in h5

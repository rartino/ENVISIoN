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

import unittest

import os, sys

# Configuration
PATH_TO_parser=os.path.expanduser("~/ENVISIoN/envision/envision/parser/vasp")

sys.path.insert(0, os.path.expanduser(PATH_TO_parser))

from .unitcell import *

#import envision.inviwo

#import h5py
#import re
#import numpy as np
#from ..h5writer import _write_volume
#from ..h5writer import _write_basis
#from ..h5writer import _write_scaling_factor
#from .unitcell import _parse_lattice



sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION))


#inherit from unittest.TestCase
class TestPKFparser(unittest.TestCase):
    #def setUp(self):
    #   pass

    def test_pathway(self):
        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main()


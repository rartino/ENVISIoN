import os, sys

# Configuration
PATH_TO_ENVISION=os.path.expanduser("~/PROJLAB/ENVISIoN/envision")
PATH_TO_VASP_CALC=os.path.expanduser("~/PROJLAB/ENVISIoN/data/parV")
PATH_TO_HDF5=os.path.expanduser("~/PROJLAB/ENVISIoN/demo.hdf5")

sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION))

import envision
#import envision.inviwo

#If a POSCAR file is missing, it's possible to take POSCAR-equivalent data from another file
#by passing the file name as an optional third argument to parchg.

envision.parser.vasp.parchg(PATH_TO_HDF5, PATH_TO_VASP_CALC)

import os, sys

# Configuration
PATH_TO_ENVISION=os.path.expanduser("~/PROJLAB/ENVISIoN/envision")
PATH_TO_VASP_CALC=os.path.expanduser("~/PROJLAB/ENVISIoN/data/parV")
PATH_TO_HDF5=os.path.expanduser("~/Desktop/demo.hdf5")

sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION))

import envision
import envision.inviwo

#To switch between datasets 1 and 2, pass 1 or 2 as a third argument to parchg (1 is default).
#If a POSCAR file is missing, it's possible to take POSCAR-equivalent data from another file
#by passing the file name as an optional fourth argument to parchg.

#envision.parser.vasp.unitcell(PATH_TO_HDF5, PATH_TO_VASP_CALC)
envision.parser.vasp.parchg(PATH_TO_HDF5, PATH_TO_VASP_CALC, 1)

#envision.inviwo.unitcell(PATH_TO_HDF5, xpos = 0)
envision.inviwo.parchg(PATH_TO_HDF5, sli = False, parchg_list = [56, 81] , xstart_pos = 600, ystart_pos = 0)

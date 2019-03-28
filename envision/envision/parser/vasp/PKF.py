import os
import sys
import itertools
import h5py
import numpy as np

# make module available
PATH_TO_parser = os.path.expanduser("~/ENVISIoN/envision/envision/parser")
sys.path.append(os.path.abspath(PATH_TO_parser))

import h5writer

# The function script from inviwo will call with envision.parser.vasp.paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)
print("This is the start of PKF!")


def paircorrelation(h5file, vasp_dir):
    #	The function is called from ENVISIoNs (alt.inviwo) environment to parse relevant information 		for visualization of the paircorrelation function.

    #	Parameters
    #	__________
    #	h5file: str
    #		String that asserts which HDF5-file to write to.

    #	vasp_dir: str
    #		Path to directory containing VASP-files, such as PCDAT.

    #	Return
    #	_______
    #	bool
    #		True if parsing is taking place, False otherwise.

    # Check if it's parsed, no need for parsing if it's already done.
    #if os.path.isfile(h5file):
       # with h5py.File(h5file, 'r') as h5:
         #   if '/PairCorrelationFunc' in h5:
        #        print('PCDAT already parsed. Skipping.')
       #         return False

    #try:
     #   with open(os.path.join(vasp_dir, 'PCDAT'), 'r') as PcdatFileObj:
      #      pass
            #pcdat_data = _parse_pcdat(h5file, PcdatFileObj)


#	except FileNotFoundError:
#		print("PCDAT file not in directory. Skipping.")
#		return False

#   except StopIteration:
#       print("PCDAT file empty. Skipping")
#       return False

# Write to HDF5 file
#	_write_pcdat(h5file, pcdat_data)
#	print('PCDAT data was parsed sucessfully.')
#	return True


# _parse_pcdat(h5file, vasp_fileobj)
# _write_pcdat(h5file, pcdat_data) pcdat_data is a list for relevant atom n.

def _parse_pcdat(h5file, vasp_fileobj):
# print("hoh")
#	print("trying")
#   The function parse PCDAT and is called upon by paircorrelation(h5file, vasp_dir)

#    Parameters
#    __________
#    h5file: str
#        String containing path to HDF5-file.

#    vasp_fileobj:
#        Is a fileobject.

#    Return
#    ______
#    a list of values.

#	Läs hur många atomslag som finns

#	line = next(vasp_fileobj)

#  header = { "Highest energy": float(line.split()[0]),
#         "Lowest energy": float(line.split()[1]),
#         "ndos": int(line.split()[2]),
#         "Fermi energy": float(line.split()[3]),
#         "weight": float(line.split()[4]) }

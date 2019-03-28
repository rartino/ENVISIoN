import os
import sys
import itertools
import h5py
import numpy as np

# make module available
PATH_TO_HDF5 = os.path.expanduser("~/ENVISIoN/HDF5/demo.hdf5")
PATH_TO_VASP_CALC = os.path.expanduser("~/ENVISIoN/data/VASP-files2019/Cu/1/10")
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
#   dict or False.
#   Function returns False when parsing fails.
#   A dictionary with the appearance {'element_type':[PKF_values]}. PKF_values are the average number of atoms, of specific element_type. If the system has elements 'Si', 'Au' and 'K', the dictionary will look like {'Si':float[x], 'Au':float[x], 'K':float[x]} where the float[x] is a list with the PKF values.

    with open(vasp_file, "r") as vasp_fileobj:
        line = next(vasp_fileobj)
        line = next(vasp_fileobj)
        line = next(vasp_fileobj) #Third line specify which elements are in the system
        
        # See if PCDAT has relevant information?
        element_list = line.split()
        if element_list[0]=="unknown" and element_list[1]=="system":
            print("Parsing of PCDAT abort! File doesn't contain relevant information. Skipping.")
            return False
        else:
            pcdat_data = {}
            total_elements = len(element_list)
            for i in range(total_elements):
                pcdat_data[element_list[i]] = []
                #To make a dictionary of the appearance {'Si':[], 'Au':[]...}
            
                
            #fill the dictionary pcdat_data
            for row_num, content in enumerate(vasp_fileobj, 3):
                if row_num >= 12: #Values from PKF
                    
                    #takes the PKF value columnwise.
                    #The first iteration for example gives
                    #{'Si':[PKF_row1column1], 'Au':[PKF_row1column2], 'K':[PKF_row1column3]...}
                    for column_num in range(total_elements):
                        PKF_value = float(content.split()[column_num])
                        #dict_key is example 'Si'
                        dict_key = element_list[column_num]
                        #Fill the pcdat_data dictionary
                        pcdat_data[dict_key].append(PKF_value)

        return pcdat_data


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

#See if parsing fails?
#See if parsing is already done? Skipping.
    vasp_file = os.path.join(vasp_dir, "PCDAT.dms")
    dict = _parse_pcdat(h5file, vasp_file)


paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)



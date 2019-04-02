import os
import sys
import h5py
import numpy as np

# make module available
PATH_TO_HDF5 = os.path.expanduser("~/ENVISIoN-gui-dev/HDF5/demo_PKF.hdf5")
PATH_TO_VASP_CALC = os.path.expanduser("~/VASP_files/Cu-DoS/Cu/1/10")

PATH_TO_parser_vasp = os.path.expanduser("~/ENVISIoN-gui-dev/envision/envision/parser/vasp")
PATH_TO_parser = os.path.expanduser("~/ENVISIoN-gui-dev/envision/envision/parser")
sys.path.append(os.path.abspath(PATH_TO_parser))  # För att h5writer ska klassas som en python modul

import h5writer
from unitcell import _find_elements
from incar import parse_incar


def _parse_pcdat(h5file, vasp_file, vasp_dir):
    #   The function parse PCDAT-file and is called upon by paircorrelation(h5file, vasp_dir)
    
    #    Parameters
    #    __________
    #    h5file: str
    #        String containing path to HDF5-file.
    
    #    vasp_file: str
    #        Is the path to vasp-file PCDAT.
    #
    #    vasp_dir: str
    #        Is the path to directory for all the VASP files.
    #
    #    Return
    #    ______
    #       pcdat_data: dict
    #           A python dictionary containing data from PCDAT-file.
    #       Bool: False is parsing fails.
    #
    #   pcdat_data is a dictionary with the appearance {'element_type':[PKF_values]}. PKF_values are the average number of atoms, of specific element_type. If the system has elements 'Si', 'Au' and 'K', the dictionary will look like {'Si':float[x], 'Au':float[x], 'K':float[x]} where the float[x] is a list with the PKF values.
    
    with open(vasp_file, "r") as vasp_fileobj:
        # See if PCDAT has the pair correlation function
        elements = None
        with open(os.path.join(vasp_dir, "POSCAR"), "r") as f:
            # _find_elements look for element symbols in POTCAR and POSCAR
            element_list, void = _find_elements(f, elements, vasp_dir)
        
        pcdat_data = {}
        total_elements = len(element_list)
        for i in range(total_elements):
            pcdat_data[element_list[i]] = []
        # To make a dictionary of the appearance {'Si':[], 'Au':[]...}
        
        # fill the dictionary pcdat_data
        count_eof = 0
        for row_num, content in enumerate(vasp_fileobj):
            count_eof = row_num
            
            if row_num >= 12:
                # takes the PKF value columnwise.
                # The first iteration for example gives
                # {'Si':[PKF_row1column1], 'Au':[PKF_row1column2], 'K':[PKF_row1column3]...}
                for column_num in range(total_elements):
                    PKF_value = float(content.split()[column_num])
                    # dict_key is example 'Si'
                    dict_key = element_list[column_num]
                    # Fill the pcdat_data dictionary
                    pcdat_data[dict_key].append(PKF_value)

    if count_eof <= 11:
        raise Exception("PCDAT-file is empty.")


    return pcdat_data


def _write_pcdat(h5file, pcdat_data, APACO_val, NPACO_val):
    #   The function is called to write data from PCDAT to HDF5-file. A dataset is created for each element in the system.
    
    #    Parameters
    #    __________
    #    h5file: str
    #        String containing path to HDF5-file.
    
    #    pcdat_data:
    #        Is a dictionary with the structure {'element_type':[PKF_values]}. PKF_values are the average number of atoms, of specific element_type. If the system has elements 'Si', 'Au'       and 'K', the dictionary will look like {'Si':float[x], 'Au':float[x], 'K':float[x]} where the float[x] is a list with the PKF values.
    #
    #    APACO_val:
    #        The value of APACO in INCAR if set, default value 16 (Å), otherwise. It sets the maximum distance in the evaluation of the pair-correlation function
    #
    #    NPACO_val:
    #        The value of NPACO in INCAR if set, default value 256 slots otherwise. It sets the number of slots in the pair-correlation function written to PCDAT.
    
    #    Return
    #    ______
    #    Bool: True if parsed, False otherwise.
    
    with h5py.File(h5file, "a") as h5:
        dset_name = "PairCorrelationFunc/Iterations"
        value = np.array([APACO_val, NPACO_val])
        h5.create_dataset(dset_name, data=value, dtype=np.float32)
        
        
        # create dataset for every element
        for n in range(len(pcdat_data)):
            # By making a dict a list, it's keys are accessable
            element_symbol = list(pcdat_data)[n]
            dset_name = "PairCorrelationFunc/Elements/{}".format(element_symbol)
            value = np.asarray(pcdat_data[element_symbol])
            dset = h5.create_dataset(dset_name, data=value, dtype=np.float32)
            h5[dset_name].attrs["element"] = element_symbol


    return None


def paircorrelation(h5file, vasp_dir):
    #   The function which script from inviwo will call with the command:  envision.parser.vasp.paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)
    #
    #    Parameters
    #    __________
    #    h5file: str
    #        String containing path to HDF5-file.
    
    #    vasp_dir:
    #        Is a path to the directory where VASP-files are.
    
    #    Return
    #    ______
    #    Bool: True if parsed, False otherwise.
    
    vasp_file = os.path.join(vasp_dir, "PCDAT.dms")
    
    # See if parsing is already done? If so skip.
    if os.path.isfile(h5file):
        with h5py.File(h5file, "r") as h5:
            if "/PairCorrelationFunc" in h5:
                x = list(h5['PairCorrelationFunc'].keys())
                print(x)
                print("Already parsed. Skipping.")
                return False

    # See if APACO and NPACO is set, otherwise default value is used.
    incar_file = os.path.join(vasp_dir, "INCAR")
    incar_data = parse_incar(h5file, incar_file)

    try:
        NPACO_val = incar_data["NPACO"]
        
    except KeyError:
        NPACO_val = 256 #default value

    try:
        APACO_val = incar_data["APACO"]
        
    except KeyError:
        APACO_val = 16 #default value


    try:
        pcdat_data = _parse_pcdat(h5file, vasp_file, vasp_dir)
        _write_pcdat(h5file, pcdat_data, APACO_val, NPACO_val)
        return True
        
    except FileNotFoundError:
        print("PCDAT file not found.")
        return False
        


paircorrelation(PATH_TO_HDF5, PATH_TO_VASP_CALC)




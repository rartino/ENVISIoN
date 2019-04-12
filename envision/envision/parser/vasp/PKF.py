import os
import sys
import h5py
import numpy as np

from .incar import _parse_incar
from .unitcell import _find_elements
from ..h5writer import _write_pcdat_onecol 
from ..h5writer import _write_pcdat_multicol

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


      is_pcdatformat_onecol = False 

      if total_elements > 1:       
        count = 0
        while count <= 12:
          count = count + 1 
          line = vasp_fileobj.readline()
  
        vasp_fileobj.seek(0,0) #Set the offset, to begin reading from start again
              
        if len(line.split()) == 1: #If there is only one column, average PCF for multiple elements. 
          is_pcdatformat_onecol = True
     
      
      if is_pcdatformat_onecol: 
      # In case of multiple elements but only one column in PCDAT-file
      # create dictinary of appearance {'general paircorr':[]}. 
        pcdat_data['general paircorr'] = []
        # fill the dictionary pcdat_data
        count_eof = 0
        for row_num, content in enumerate(vasp_fileobj):
          count_eof = row_num
          if row_num >= 12:
            PKF_value = float(content.split()[0])
            pcdat_data['general paircorr'].append(PKF_value)
 
        if count_eof <= 11:
          raise Exception("PCDAT-file is empty.")

        return pcdat_data
          
      
      else:     
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

  return pcdat_data


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

  vasp_file = os.path.join(vasp_dir, "PCDAT")

    # See if parsing is already done? If so skip.
  if os.path.isfile(h5file):
      with h5py.File(h5file, "r") as h5:
          if "/PairCorrelationFunc" in h5:
              print("Already parsed. Skipping.")              
              htest = h5["PairCorrelationFunc"]
              print(list(htest.keys()))
              return False

    # See if APACO and NPACO is set, otherwise default value is used.
  incar_file = os.path.join(vasp_dir, "INCAR")
  incar_data = _parse_incar(h5file, incar_file)

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
    if list(pcdat_data)[0] == "general paircorr": 
      _write_pcdat_onecol(h5file, pcdat_data, APACO_val, NPACO_val)

    else: 
      _write_pcdat_multicol(h5file, pcdat_data, APACO_val, NPACO_val)

    return True

  except FileNotFoundError:
    print("PCDAT file not found.")
    return False


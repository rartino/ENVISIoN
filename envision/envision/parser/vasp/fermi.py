#Inviwo Python script
import os
import re
import h5py
import numpy as np
#from ..h5writer import _write_bandstruct

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *){4}')


def fermi_parse(vasp_dir):
    """
    Parses band structure data from EIGENVAL and Fermi energy from DOSCAR

    Parameters
    ----------
   vasp_dir : string
       string containing path to VASP-files

    Returns
    -------
    band_data : list
        list containing all the band data
    kval_list : list
        list containing all the K-points
    fermi_energy: float
        float containing the Fermi energy

    """
    data = None
    kval = None
    kval_list = []
    band_data = []
    i = 0

    eigenval_file = os.path.join(vasp_dir, 'EIGENVAL')
    with open(eigenval_file, "r") as f:
        for line in f:
            match_float = line_reg_float.match(line)
            match_int = line_reg_int.match(line)
            if match_int:
                 data = [int(v) for v in line.split()]
                 band_data = [[] for _ in range(data[2])]
            if data and match_float:
                 kval = []
                 for u in range(3):
                    kval.append(float(line.split()[u]))
            elif kval and data:
                  band_data[i].append(float(line.split()[1]))
                  i += 1
            if i == len(band_data) and kval:
                   kval_list.append(kval)
                   kval = None
                   i = 0
    #Parses fermi energy from DOSCAR
    #with open( '/home/marian/ENVISIoN/data/ZnS/VASP/DOSCAR',"r") as f:
    doscar_file = os.path.join(vasp_dir, 'DOSCAR')
    with open(doscar_file, "r") as f:
        next(f)
        next(f)
        next(f)
        next(f)
        next(f)
        line = next(f)
        fermi_energy = float(line.split()[3])

    return band_data, kval_list, fermi_energy

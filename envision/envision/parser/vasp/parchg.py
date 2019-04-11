#
#  ENVISIoN
#
#  Copyright (c) 2018 Elvis Jakobsson
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
path_to_envision = 'C:/ENVISIoN' 
import wx, sys, os
sys.path.insert(0, os.path.expanduser(path_to_envision+'/envision/envision/parser'))
sys.path.insert(0, os.path.expanduser(path_to_envision+'/envision/envision/parser/vasp'))
import re
import numpy as np
import h5py
import math
from unitcell import *
from h5writer import _write_parcharges

def _parse_parcharges(fileobj):
        """Parses partial charge data from a PARCHG.nb.ALLK file in VASP

         Parameters
         ----------
         fileobj : file object
         File to be parsed
         
         Returns
         -------
         data_dim_tot: list of int
                   list of dimensions of the partial charge data (total)
         parcharges_tot: list of float
                     list of partial charge data (total)
         data_dim_mag: list of int
                   list of dimensions of the partial charge data (magnetic)
         parcharges_mag : list of float
                     list of partial charge data (magnetic)

        """
        
        atomcount_re=re.compile('^ *(([0-9]+) *)+$')
        while True:
                atoms_per_species = next(fileobj)
                match = atomcount_re.match(atoms_per_species)
                if match:
                        break
        all_atoms = sum([int(n) for n in atoms_per_species.split()])

        for x in range(0, all_atoms+2):
                next(fileobj)

        data_dim_tot = [int(n) for n in next(fileobj).split()]
        datasize_tot = data_dim_tot[0]*data_dim_tot[1]*data_dim_tot[2]
        parcharges_tot = []

        data_dim_mag = []
        parcharges_mag = []
        

        for x in range(0, math.ceil(datasize_tot/10)):
                parcharges_tot.extend([float(n) for n in next(fileobj).split()[:10]])

        try:
                next(fileobj)
                data_dim_mag = [int(n) for n in next(fileobj).split()]
                datasize_mag = data_dim_mag[0]*data_dim_mag[1]*data_dim_mag[2]
        
                for x in range(0, math.ceil(datasize_mag/10)):
                        parcharges_mag.extend([float(n) for n in next(fileobj).split()[:10]])
                        
        except StopIteration:
                print("No magnetic charge density found. Skipping.")
        

        return data_dim_tot, data_dim_mag, np.array(parcharges_tot), np.array(parcharges_mag)

def parchg(h5file, vasp_dir, poscar_equiv='POSCAR'):
        """PARCHG parser 
        
        Reads partial charge data from PARCHG file and writes data to an HDF5 file.
        Currently only works with PARCHG files separated by band and with merged k-points.
        User is required to specify from what file to read lattice vectors and atom positions
        (POSCAR data), if that file is not a POSCAR file. This means a POSCAR file isn't 
        necessary as the same information can be extracted from the PARCHG file.

            Parameters
            ----------
            h5file : str
                Path to HDF5 file

            vasp_dir : str
                Path to directory containing POSCAR file

            poscar_equiv : str
                 (Default value = 'POSCAR')
                Name of the file from which POSCAR-equivalent data can be read. By default
                it tries to read from a POSCAR file.

            Returns
            -------
            bool
            True if PARCHG was parsed, False otherwise.
        """

        unitcell(h5file, vasp_dir)

        regex = re.compile('PARCHG.(.+?).ALLK')
        if os.path.isfile(h5file):
                with h5py.File(h5file, 'r') as h5:
                        if "/PARCHG" in h5:
                                print("Already parsed. Skipping.")
                                return False
                        h5.close()
                        
                        file_list = sorted(os.listdir(vasp_dir))
                        band_list = [string for string in file_list if re.match(regex, string)]
                        
                        for name in band_list:
                                try:
                                        with open(os.path.join(vasp_dir,name), "r") as f:
                                                data_dim_tot, data_dim_mag, parcharges_tot, parcharges_mag = _parse_parcharges(f)
                                                band_nr = re.search('PARCHG.(.+?).ALLK', name).group(1)
                                                while band_nr[0] == '0':
                                                        band_nr = band_nr[1:]
                                                _write_parcharges(h5file, parcharges_tot, data_dim_tot, parcharges_mag, data_dim_mag, band_nr)
                                
                                except FileNotFoundError:
                                        print("PARCHG file not found.")
                                        return False

                        print('PARCHG was parsed successfully.')
                        return True

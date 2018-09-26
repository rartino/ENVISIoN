import os
import re
import numpy as np
import h5py
from .unitcell import *
from ..h5writer import _write_parcharges

def _parse_parcharges(fileobj):
        """Parses partial charge data from a PARCHG.nb.ALLK file in VASP

         Parameters
         ----------
         fileobj : file object
         File to be parsed
         
         Returns
         -------
         data_dim: list of int
                   list of dimensions of the data
         parcharges: list of float
                     list of partial charge data
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

        data_dim = [int(n) for n in next(fileobj).split()]
        datasize = data_dim[0]*data_dim[1]*data_dim[2]
        parcharges = []

        for x in range(0, int(datasize/10)):
                parcharges.extend([float(n) for n in next(fileobj).split()[:10]])
                
        return data_dim, np.array(parcharges)

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

        unitcell(h5file, vasp_dir, None, poscar_equiv)

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
                                                data_dim, parcharges = _parse_parcharges(f)
                                                band_nr = re.search('PARCHG.(.+?).ALLK', name).group(1)
                                                _write_parcharges(h5file, parcharges, data_dim, band_nr)
                                
                                except FileNotFoundError:
                                        print("PARCHG file not found.")
                                        return False

                        print('PARCHG was parsed successfully.')
                        return True

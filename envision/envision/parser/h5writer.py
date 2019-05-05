#
#  ENVISIoN
#
#  Copyright (c) 2017-2019 Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström,
#  Fredrik Segerhammar, Anders Rehult, Viktor Bernholtz, Elvis Jakobsson, Abdullatif Ismail
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
#
#  Alterations to this file by Anders Rehult and Viktor Bernholtz
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
##############################################################################################
#
#  Alterations to this file by Abdullatif Ismail
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import numpy as np
import h5py
import array as arr


def _write_coordinates(h5file, atom_count, coordinates_list, elements, path):
    with h5py.File(h5file, "a") as h5:
        p=0
        for n in range(0,len(atom_count)):
            dataset_name = path+'/Atoms/'+format(n,'04d')
            h5.create_dataset(
                dataset_name,
                data=np.asarray(coordinates_list[p:atom_count[n]+p]),
                dtype=np.float32
            )
            h5[dataset_name].attrs["element"] = elements[n]
            p=p+atom_count[n]
    return

def _write_basis(h5file, basis):
    with h5py.File(h5file, "a") as h5:
        if not "/basis" in h5:
            h5.create_dataset('/basis', data=basis, dtype=np.float32)
    return

def _write_scaling_factor(h5file, scaling_factor):
    with h5py.File(h5file, "a") as h5:
        if not "/scaling_factor" in h5:
            h5.create_dataset('/scaling_factor', data=scaling_factor, dtype=np.float32)
    return

def _write_md(h5file, atom_count, coordinates_list, elements, step):
    with h5py.File(h5file, "a") as h5:
        p=0
        for n in range(0,len(atom_count)):
            dataset_name = '/MD/Atoms/'+format(n,'04d')
            if step == 0:
                h5.create_dataset(
                    dataset_name,
                    data=np.asarray(coordinates_list[p:atom_count[n]+p]),
                    dtype=np.float32,
                    maxshape=(None, 3)
                )
                h5[dataset_name].attrs["element"] = elements[n]
                h5[dataset_name].attrs["atoms"] = atom_count[n]
                p=p+atom_count[n]
            else:
                dataset = h5[dataset_name]
                dataset.resize((step+1)*atom_count[n],axis=0)
                start = step*atom_count[n]
                dataset[start:] = np.asarray(coordinates_list[p:atom_count[n]+p])
                p=p+atom_count[n]
    return

def _write_steps(h5file, steps):
    with h5py.File(h5file, "a") as h5:
        h5['/MD'].attrs["steps"] = steps
    return

def _write_bandstruct(h5file, band_data, kval_list):
    with h5py.File(h5file, "a") as h5:
        h5.create_dataset('BandStructure/KPoints', data=np.array(kval_list), dtype = np.float32)
        for i, band in enumerate(band_data):
            dataset = h5.create_dataset('Bandstructure/Bands/{}/{}'.format(i, 'Energy'), data=np.array(band), dtype = np.float32)
            dataset.attrs['Unit'] = 'eV'
            dataset.attrs['QuantitySymbol'] = '$E$'
            dataset.attrs['QuantityName'] = 'Energy'
            dataset.attrs['VariableName'] = 'Band {}'.format(i)
            dataset.attrs['VariableSymbol'] = '$B_{{{}}}$'.format(i)

def _write_fermi_energy(h5file, fermi_energy):
    with h5py.File(h5file,"a") as h5:
        h5.create_dataset('/FermiEnergy',
                          data = np.float(fermi_energy),
                          dtype = np.float32)


def _write_fermisurface(h5file, kval_list, fermi_energy, reciprocal_lattice_vectors):
    with h5py.File(h5file,"a") as h5:
        for i in range(0, len(kval_list)):
            dataset = h5.create_dataset('/FermiSurface/KPoints/{}/Energy'.format(i),
                                        data = np.array(kval_list[i].energies),
                                        dtype = np.float32)
            dataset.attrs['Unit'] = 'eV'
            dataset.attrs['QuantitySymbol'] = '$E$'
            dataset.attrs['QuantityName'] = 'Energy'
            dataset.attrs['VariableName'] = 'Band {}'.format(i)
            dataset.attrs['VariableSymbol'] = '$B_{{{}}}$'.format(i)

            h5.create_dataset('/FermiSurface/KPoints/{}/Coordinates'.format(i),
                              data = np.array(kval_list[i].coordinates),
                              dtype = np.float32)
            
        if '/FermiEnergy' in h5:
            print('Fermi energy already parsed. Skipping.')
        else:
            _write_fermi_energy(h5file, fermi_energy)


        for i in range(0, len(reciprocal_lattice_vectors)):
            h5.create_dataset('/FermiSurface/ReciprocalLatticeVectors/{}'.format(i),
                              data = np.array([float(x) for x in reciprocal_lattice_vectors[i]]),
                              dtype = np.float32)


def _write_dos(h5file, total, partial, total_data, partial_list, fermi_energy):

    def set_attrs(dataset, VariableName = '', VariableSymbol = '', QuantityName = '', QuantitySymbol = '', Unit = ''):
        dataset.attrs.update({
            'VariableName' : VariableName,
            'VariableSymbol' : VariableSymbol,
            'QuantityName' : QuantityName,
            'QuantitySymbol' : QuantitySymbol,
            'Unit' : Unit
        })

    with h5py.File(h5file, "a") as h5:
        dataset = h5.create_dataset('FermiEnergy', data = np.array(fermi_energy), dtype = np.float32)
        set_attrs(dataset, 'Fermi Energy', '$E_f$', 'Energy', '$E$', 'eV')
        for i, (name, data) in enumerate(zip(total, total_data)):
            dataset = h5.create_dataset('DOS/Total/{}'.format(name), data=np.array(data), dtype = np.float32)
            if name == 'Energy':
                set_attrs(dataset, 'Energy', '$E$', 'Energy', '$E$', 'eV')
            else:
                if name.startswith('Integrated'):
                    set_attrs(dataset, name, '', 'Integrated Density of States', '$\\int D$', 'states')
                else:
                    set_attrs(dataset, name, '', 'Density of States', '$D$', 'states/eV')
        for i, partial_data in enumerate(partial_list):
            # Write all available DOS. Stop when partial or partial_data runs out (if directories for for example f-DOS
            # exist but no corresponding data exists, stop.)
            for (name, data) in zip(partial, partial_data):
                dataset = h5.create_dataset('DOS/Partial/{}/{}'.format(i, name), data=np.array(data), dtype = np.float32)
                if name == 'Energy':
                    set_attrs(dataset, 'Energy', '$E$', 'Energy', '$E$', 'eV')
                else:
                    if name.startswith('Integrated'):
                        set_attrs(dataset, name, '', 'Integrated Density of States', '$\\int D$', 'states')
                    else:
                        set_attrs(dataset, name, '', 'Density of States', '$D$', 'states/eV')

def _write_volume(h5file, i, array, data_dim, hdfgroup):
    with h5py.File(h5file, "a") as h5:
        if array:
            h5.create_dataset('{}/{}'.format(hdfgroup, i), data = np.reshape(array, (data_dim[2],data_dim[1],data_dim[0])), dtype=np.float32)
        else:
            h5['{}/final'.format(hdfgroup)] = h5['{}/{}'.format(hdfgroup, i-1)]
    return


def _write_incar(h5file, incar_data):
    with h5py.File(h5file, 'a') as h5:
        for key, value in incar_data.items():
            h5.create_dataset("/incar/{}".format(key), data=value)

def _write_parcharges(h5file, array_tot, data_dim_tot, array_mag, data_dim_mag, band_nr):
    with h5py.File(h5file, "a") as h5:
        h5.create_dataset('PARCHG/Bands/{}/total'.format(band_nr), data = np.reshape(array_tot, (data_dim_tot[2],data_dim_tot[1],data_dim_tot[0])), dtype=np.float32)
        if not np.size(array_mag) == 0:
            h5.create_dataset('PARCHG/Bands/{}/magnetic'.format(band_nr), data = np.reshape(array_mag, (data_dim_mag[2],data_dim_mag[1],data_dim_mag[0])), dtype=np.float32)
    return

def _write_pcdat_multicol(h5file, pcdat_data, APACO_val, NPACO_val):
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


    with h5py.File(h5file, 'a') as h5:
        dset_name = "PairCorrelationFunc/Iterations"
        normal_arr = arr.array('f', [])

        #creating x-values, equally spaced (space APACO_val/NPACO_val)
        for i in range(0, NPACO_val):
            x = (APACO_val / NPACO_val) * i
            normal_arr.append(x)
        value = np.asarray(normal_arr)
        h5.create_dataset(dset_name, data=value, dtype=np.float64)

        # create dataset for paircorrelation function for every time frames for every element.
        #len(pcdat_data) gives the amount of elements
        for n in range(len(pcdat_data)):
            # By making a dict a list, its keys are accessable.
            element_symbol = list(pcdat_data)[n]
            dset_groupname = "PairCorrelationFunc/Elements/{}".format(element_symbol)
            #Iterate for every time frame.
            original_list = pcdat_data[element_symbol]
            ioriginal_list = pcdat_data[element_symbol]

            for t_value in range(len(original_list)):
                fill_list = []
                for i in range(NPACO_val):
                    fill_list.append(original_list[0])
                    del original_list[0]

                tmp_name = str(dset_groupname) + "/{}"
                dset_name2 = tmp_name.format("t_" + str(t_value))
                h5.create_dataset(dset_name2, data=np.array(fill_list), dtype=np.float64)
                h5[dset_name2].attrs["element"] = element_symbol


                if len(original_list) == 0:
                    break
                else:
                    del original_list[0]



            # if NPACO= 256, there are 3 time frames (t1,t2 and t3).



    return None

def _write_pcdat_onecol(h5file, pcdat_data, APACO_val, NPACO_val):

    with h5py.File(h5file, 'a') as h5:
        dset_name = "PairCorrelationFunc/Iterations"
        normal_arr = arr.array('f', [])

        #creating x-values, equally spaced (space APACO_val/NPACO_val)
        for i in range(0, NPACO_val):
            x = (APACO_val / NPACO_val) * i
            normal_arr.append(x)
        value = np.asarray(normal_arr)
        h5.create_dataset(dset_name, data=value, dtype=np.float64)

        # create dataset for paircorrelation function for every time frames for every element.
        #len(pcdat_data) gives the amount of elements
        # By making a dict a list, its keys are accessible.

        #Iterate for every time frame.
        original_list = pcdat_data["general paircorr"]

        for t_value in range(len(original_list)):
            fill_list = []
            for i in range(NPACO_val):
                fill_list.append(original_list[0])
                del original_list[0]

            dset_name2 = "PairCorrelationFunc/{}".format("t_" + str(t_value))
            h5.create_dataset(dset_name2, data=np.array(fill_list), dtype=np.float64)


            if len(original_list) == 0:
                break
            else:
                del original_list[0]



            # if NPACO= 256, there are 3 time frames (t1,t2 and t3).


    return None
        







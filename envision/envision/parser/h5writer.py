#
#  ENVISIoN
#
#  Copyright (c) 2017 Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar
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
import numpy as np
import h5py


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
        h5.create_dataset('Bandstructure/KPoints', data=np.array(kval_list), dtype = np.float32)
        for i, band in enumerate(band_data):
            dataset = h5.create_dataset('Bandstructure/Bands/{}/{}'.format(i, 'Energy'), data=np.array(band), dtype = np.float32)
            dataset.attrs['Unit'] = 'eV'
            dataset.attrs['QuantitySymbol'] = '$E$'
            dataset.attrs['QuantityName'] = 'Energy'
            dataset.attrs['VariableName'] = 'Band {}'.format(i)
            dataset.attrs['VariableSymbol'] = '$B_{{{}}}$'.format(i)

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
            
def _write_incar(h5file, incar_data):
    with h5py.File(h5file, 'a') as h5:
        for key, value in incar_data.items():
            h5.create_dataset("/incar/{}".format(key), data=value)

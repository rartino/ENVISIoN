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
	
def _write_bandstruct(h5file, eigenval, kval_list):
    with h5py.File(h5file, "a") as h5:
        h5.create_dataset('Bandstructure/KPoints', data=np.reshape(kval_list, (40, 3)), dtype = np.float32)
        for band in eigenval:
            dataset = h5.create_dataset('Bandstructure/Bands/{}'.format(eigenval.index(band)), data=np.array(band), dtype = np.float32)
            dataset.attrs['Unit'] = 'eV'
            dataset.attrs['QuantitySymbol'] = 'E'
            dataset.attrs['QuantityName'] = 'Energy'
            dataset.attrs['VariableName'] = 'Band {}'.format(eigenval.index(band))
            dataset.attrs['VariableSymbol'] = 'B{}'.format(eigenval.index(band))

def _write_dos(h5file, total, partial, total_data, partial_list, fermi_energy):
	i = 0
	with h5py.File(h5file, "a") as h5:
		h5.create_dataset('FermiEnergy', data = np.array(fermi_energy), dtype = np.float32)
		for element in total_data:
			h5.create_dataset('Total/' + total[i], data=np.array(element), dtype = np.float32)
			i += 1		
		for partial_data in partial_list:
			u = 0
			for element in partial_data:
				h5.create_dataset('Partial/{}'.format(partial_list.index(partial_data)) + '/' + partial[u], data=np.array(element), dtype = np.float32)
				u += 1

def _write_volume(h5, i, array, data, volume):
	h5.create_dataset(volume +'/{}'.format(i,'04d'), data = np.reshape(array, (data[2],data[1],data[0])), dtype=np.float32)

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

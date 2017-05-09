import numpy as np
import h5py


def _write_coordinates(h5fileobj, atom_count, coordinates_list, elements, path):
    p=0
    for n in range(0,len(atom_count)):
        dataset_name = path+'/Atoms/'+format(n,'04d')
        h5fileobj.create_dataset(dataset_name, data=np.asarray(coordinates_list[p:atom_count[n]+p]), dtype=np.float32)
        h5fileobj[dataset_name].attrs["element"] = elements[n]
        p=p+atom_count[n]
    return

def _write_unitcell(h5file, scaling_factor, basis, atom_count, coord_list, elements, cartesian=False):
    with h5py.File(h5file, "a") as h5:
        h5.create_dataset('/UnitCell/basis', data=np.asarray(basis), dtype=np.float32)
        h5.create_dataset('/UnitCell/scaling_factor', data=scaling_factor, dtype=np.float32)
        _write_coordinates(h5, atom_count, coord_list, elements, '/UnitCell')
        h5['/UnitCell'].attrs["cartesian"] = cartesian
    return

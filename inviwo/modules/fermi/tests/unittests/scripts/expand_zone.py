import numpy as np

from HDF5FermiSource import HDF5FermiSource

process = HDF5FermiSource('fermi', 'fermi_source')

mat4 = np.zeros((4, 4, 4))
mat8 = process.expand(mat4)

status = (mat8.shape == (8, 8, 8))

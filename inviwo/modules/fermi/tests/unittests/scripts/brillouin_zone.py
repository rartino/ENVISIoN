import numpy as np

from HDF5FermiSource import HDF5FermiSource

process = HDF5FermiSource('fermi', 'fermi_source')

mat4 = np.zeros((10, 10, 10))
basis = 0.2*np.eye(3)

brill = process.brillouin_zone(mat4, basis)

lenx = int(brill.shape[0]/2)
leny = int(brill.shape[1]/2)
lenz = int(brill.shape[2]/2)

# Basically just testing values around the brillouin zone border
# might be a better way of testing all values inside/outside brillouin zone
status = (
    brill.shape == (20, 20, 20) and
    # values inside brillouin zone are 0.0
    brill[lenx, leny, lenz] == 0.0 and
    # lower end
    brill[int(lenx*1/2) + 1, leny, lenz] == 0.0 and
    brill[lenx, int(leny*1/2) + 1, lenz] == 0.0 and
    brill[lenx, leny, int(lenz*1/2) + 1] == 0.0 and
    # upper end
    brill[int(lenx*3/2) - 1, leny, lenz] == 0.0 and
    brill[lenx, int(leny*3/2) - 1, lenz] == 0.0 and
    brill[lenx, leny, int(lenz*3/2) - 1] == 0.0 and

    # values outside brillouin zone are 1.0
    brill[0, 0, 0] == 1.0 and
    # lower end
    brill[int(lenx*1/2) - 1, leny, lenz] == 1.0 and
    brill[lenx, int(leny*1/2) - 1, lenz] == 1.0 and
    brill[lenx, leny, int(lenz*1/2) - 1] == 1.0 and
    # upper end
    brill[int(lenx*3/2) + 1, leny, lenz] == 1.0 and
    brill[lenx, int(leny*3/2) + 1, lenz] == 1.0 and
    brill[lenx, leny, int(lenz*3/2) + 1] == 1.0
)

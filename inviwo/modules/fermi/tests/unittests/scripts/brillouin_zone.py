#
#  ENVISIoN
#
#  Copyright (c) 2020 Alexander Vevstad
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

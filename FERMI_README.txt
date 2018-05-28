Regarding the Fermi processor in the fermi module
=================================================

The Fermi-Surface processor in the fermi module is not done. Currently
it is capable of loading fermi data from the HDF5 file, but the
visualisation itself isn't correct.

One point that was discussed for verifying if it reads points
correctly, was modifying it to visualise single points from k-space
data where the positions of loaded points would be known in advance
and the positioning could be verified.

Building
========

The processor uses a library called einspline. To build it, that
library is requried. It can be found at
http://einspline.sourceforge.net/ along with installation
instructions.

If Inviwo complains that the library is missing, even though it is
installed:

"./bin/inviwo: error while loading shared libraries: libeinspline.so.0: cannot open shared object file: No such file or directory"

The solution is to manually pass it the path where einspline is
installed:

LD_LIBRARY_PATH=/usr/local/lib ./bin/inviwo

It is also possible to manually symlink the library from
/usr/local/lib to /lib.

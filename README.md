# ENVISIoN: Electronic Structure Visualization Studio

ENVISIoN is an open source tool/toolkit for electron visualization.

ENVISIoN is implemented using (a modified version of) the Inviwo visualization framework, developed at the Scientific Visualization Group at Linköping University (LiU).

The present version was developed during the spring term of 2019 by a project group consisting of: Linda Le, Abdullatif Ismail, Anton Hjert, Lloyd Kizito and Jesper Ericsson. Supervisor: Johan Jönsson; Requisitioner and co-supervisor: Rickard Armiento; Visualization expert: Peter Steneteg; and Course examiner: Per Sandström.

The initial version was developed as part of the course TFYA75: Applied Physics - Bachelor Project, given at Linköping University, Sweden (LiU) spring term 2017. The title of the final report was: "Design och implementing av en interakiv visualisering av elektronstrukturdata". Authors: Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar. The project was supervised by Johan Jönsson (main supervisor), Rickard Armiento (expert and client), and Peter Steneteg (expert). The course examinator was Per Sandström.

Subsequent contributions have been made during the spring term of 2018 by Anders Rehult, Andreas Kempe, Marian Brännvall, and Viktor Bernholtz, as part of the same course. The title of the final report was: "Design och implementering av system för interaktiv visualisering av elektronstrukturdata". The project was supervised by Johan Jönsson (main supervisor) and Rickard Armiento (client and expert). The course examinator was Per Sandström.

ENVISIoN provides a graphical user interface and a set of Python scripts that allow the user to:

- Read and parse output from electronic structure codes (presently VASP, and some support for Elk is implemented), storing the result in a structured HDF5 file.
- Generate interactive Inviwo visualization networks for
  tasks common when analyzing electronic structure calculations.
  Presently there is (to varying degree) support for crystal structures,
  ab-inito molecular dynamics, charge density, ELF, DOS/pDOS and
  band structure visualization.

## Installing ENVISIoN from source

This guide will step by step show how to build Inviwo and thereafter install ENVISIoN from source using Ubuntu 18.04. Installing and building on other platforms should be simmilar but dependencies and specific commands may vary.

### Install dependencies

Git:
```
  sudo apt-get install git
```

Inviwo dependencies:
```
sudo apt install build-essential \
    libpython3-dev libpython3-dbg \
    mesa-common-dev libglu1-mesa-dev \
    libxcursor-dev libxinerama-dev libxrandr-dev \
    qtchooser libzma-dev python3-distutils gcc-8 g++-8 gfortran-8
```

Install cmake. As of writing this the version supplied by Ubuntu apt-get is not compatible with Inviwo, install latest version of cmake manually.
Uninstall package managed cmake:
```
sudo apt purge --auto-remove cmake
```

Download and install latest cmake version into /opt/cmake/:

```
version=3.15
build=2
mkdir ~/temp
cd ~/temp
wget https://cmake.org/files/v$version/cmake-$version.$build-Linux-x86_64.sh 
sudo mkdir /opt/cmake
sudo sh cmake-$version.$build-Linux-x86_64.sh --prefix=/opt/cmake
```

Add the installed binary link to /usr/local/bin/cmake by running this:
´´´
sudo ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
´´´

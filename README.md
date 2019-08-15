# ENVISIoN: Electronic Structure Visualization Studio

ENVISIoN is an open source tool/toolkit for electron visualization. 
ENVISIoN can be used to visualise the following.
* Electron density
* Electron localisation function
* Partial charge density
* Unitcell
* Bandstructure
* Density of states
* Pair correlation function

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

Inviwo dependencies via package manager:
```
sudo apt install \ 
  git build-essential gcc \
  python3-dev python3-pip python-wxgtk4.0
  nodejs npm
  libpng-dev libglu1-mesa-dev libxrandr-dev \
  libhdf5-dev libxinerama-dev libxcursor-dev                 
```


Install cmake. As of writing this the version supplied by Ubuntu apt-get is not compatible with Inviwo, install latest version of cmake manually.
Uninstall package managed cmake:
```
sudo apt purge --auto-remove cmake
```

Download and install latest cmake version into /opt/cmake/:
```
mkdir ~/temp
cd ~/temp
wget https://cmake.org/files/v3.15/cmake-3.15.2-Linux-x86_64.sh 
sudo mkdir /opt/cmake
sudo sh cmake-$version.$build-Linux-x86_64.sh --prefix=/opt/cmake
```

Verify that cmake was installed by running `cmake -version` 

Add the installed binary link to /usr/local/bin/cmake by running this:
```
sudo ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
```

Verify that Qt was installed  by running `qmake -version`

Install Qt5. ENVISIoN is tested using version Qt 5.12.2 but should work on any Qt after 5.6.1.
```
wget http://download.qt.io/official_releases/qt/5.12/5.12.2/qt-opensource-linux-x64-5.12.2.run
chmod +x qt-opensource-linux-x64-5.12.2.run
sudo ./qt-opensource-linux-x64-5.12.2.run
qtchooser -install Qt5.12.2 /opt/Qt5.12.2/12.2/gcc_64/bin/qmake
```

Install required python modules:
```
pip3 install numpy scipy h5py regex matplotlib pybind11
```

###Clone ENVISIoN
```
git clone https://github.com/rartino/ENVISIoN
```

###Build Inviwo
Start by cloning the Inviwo source code. Also check out a compatible version. Later versions may work but are not tested.
```
git clone https://github.com/inviwo/inviwo.git
cd inviwo
git checkout 400de1a5af6a0400a314241b86982cfa2817dd9b
git submodule update --init --recursive
```

Apply ENVISIoN patches to inviwo (paths may vary depending on where you cloned ENVISIoN).
```
cd inviwo
git apply /home/ENVISIoN/inviwo/patches/2019/transferfunctionFix.patch
git apply /home/ENVISIoN/inviwo/patches/2019/deb-package.patch
```

Setup build directory.
```
mkdir inviwo-build
cd inviwo-build
```

Generate makefiles with cmake. Again specific paths may vary depending on where things were installed.
```
cmake -G "Unix Makefiles" \
  -DCMAKE_PREFIX_PATH="/opt/Qt5.12.2/12.2/gcc_64/bin/qmake" \
  -DIVW_EXTERNAL_MODULES="/home/ENVISIoN/inviwo/modules" \
  -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
  -DIVW_MODULE_FERMI=OFF \
  -DIVW_MODULE_GRAPH2D=ON \
  -DIVW_MODULE_PYTHON3=ON \
  -DIVW_MODULE_PYTHON3QT=ON \
  -DIVW_MODULE_QTWIDGETS=ON \
  -DIVW_MODULE_HDF5=ON \ 
  -DIVW_PACKAGE_PROJECT=ON \ 
  -DIVW_PACKAGE_INSTALLER=ON
```

Inviwo can now be build.
```
make -j5
```

Verify that inviwo was build by running `./bin/inviwo`. The Inviwo editor should start.




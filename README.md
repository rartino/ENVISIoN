# ENVISIoN: Electronic Structure Visualization Studio

ENVISIoN is an open source tool/toolkit for electron structure visualization. ENVISIoN provides a graphical user interface and a set of Python scripts that allow the user to visualise output data from VASP.

ENVISIoN can be used to visualise the following.
* Electron density
* Electron localisation function
* Partial charge density
* Unitcell
* Bandstructure
* Density of states and partial density of states
* Pair correlation function

ENVISIoN is developed at Linköping University (LiU) for IFM. ENVISIoN is implemented using (a modified version of) the Inviwo visualization framework, developed at the Scientific Visualization Group at LiU.

ENVISIoN is licenced under [BSD 2-Clause "Simplified" License](/LICENSE).

## Contents

* [Contributors](#contributors)
* [Installing ENVISIoN from deb package](#installing-envision-from-deb-package)
* [Installing ENVISIoN source](#installing-envision-from-source)
  * [Install dependencies](#install-dependencies)
  * [Clone ENVISIoN](#clone-envision)
  * [Build Inviwo](#build-inviwo)
  * [Configure ENVISIoN](#configure-envision)
* [Using ENVISIoN](#using-envision)
  * [Starting ENVISIoN with electron user interface](#starting-envision-with-electron-user-interface)
  * [Using ENVISIoN from Inviwo editor](#using-envision-from-inviwo-editor)
* [Building ENVISIoN as package](#building-envision-as-package)

## Contributors

Summer 2019 development was continued by Jesper Ericsson.

Spring term 2019 ENVISIoN was developed by a project group consisting of: Linda Le, Abdullatif Ismail, Anton Hjert, Lloyd Kizito and Jesper Ericsson. Supervisor: Johan Jönsson; Requisitioner and co-supervisor: Rickard Armiento; Visualization expert: Peter Steneteg; and Course examiner: Per Sandström.

Subsequent contributions have been made during the spring term of 2018 by Anders Rehult, Andreas Kempe, Marian Brännvall, and Viktor Bernholtz, as part of the same course. The title of the final report was: "Design och implementering av system för interaktiv visualisering av elektronstrukturdata". The project was supervised by Johan Jönsson (main supervisor) and Rickard Armiento (client and expert). The course examinator was Per Sandström.

The initial version was developed as part of the course TFYA75: Applied Physics - Bachelor Project, given at Linköping University, Sweden (LiU) spring term 2017. The title of the final report was: "Design och implementing av en interakiv visualisering av elektronstrukturdata". Authors: Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar. The project was supervised by Johan Jönsson (main supervisor), Rickard Armiento (expert and client), and Peter Steneteg (expert). The course examinator was Per Sandström.

## Installing ENVISIoN from deb package
Download the packaged version from the [releases page](https://pages.github.com/).

Install the deb package using your package manager.
You should now be able to start ENVISIoN using `envision` and Inviwo using `inviwo` in your terminal.

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

Install cmake, version 14 or later required. As of writing this the version supplied by Ubuntu apt-get is not compatible with Inviwo, install latest version of cmake manually.
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

Add the installed binary link to /usr/local/bin/cmake by running this:
```
sudo ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
```

Verify that cmake was installed by running `cmake -version` 

Install Qt5. ENVISIoN is tested using version Qt 5.12.2 but should work on any Qt after 5.6.1. If a Qt version after 5.6.1 is available 
```
wget http://download.qt.io/official_releases/qt/5.12/5.12.2/qt-opensource-linux-x64-5.12.2.run
chmod +x qt-opensource-linux-x64-5.12.2.run
sudo ./qt-opensource-linux-x64-5.12.2.run
qtchooser -install Qt5.12.2 /opt/Qt5.12.2/12.2/gcc_64/bin/qmake
```

Verify that Qt was installed  by running `qmake -version`

Install required python modules:
```
pip3 install numpy scipy h5py regex matplotlib pybind11
```

### Clone ENVISIoN
```
git clone https://github.com/rartino/ENVISIoN
```

### Build Inviwo
Start by cloning the Inviwo source code. Checkout a compatible version. Later versions of Inviwo may work but are not tested.
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

### Configure ENVISIoN
This can either be done by running the setup script `setup.sh` or done manually as described below.
```
cd ENVISIoN/
./setup.sh
```

If the setup script does not work or you wish to do it manually do the following:
Start by entering the ENVISIoN directory.
```
cd /home/ENVISIoN/
```

Install node modules with `npm`.
```
npm install
```

Set correct path to Inviwo binaries in `envisionpy/EnvisionMain.py`. Change the variable `PATH_INVIWO_BIN` to where your Inviwo binaries were built.

ENVISIoN should now be installed and ready to run.

## Using ENVISIoN

### Starting ENVISIoN with electron user interface
The ENVISIoN interface can be started with npm.
```
npm start
```

You should now see the main window from where ENVISIoN can be controlled.

### Using ENVISIoN from Inviwo editor
Note that this is not very user friendly and is not reccomended for most users.

ENVISIoN provides a set of scripts that can be run to start visualisations from the Inviwo application. This can be useful for developing and debuging visualisation networks or if ENVISIoNs own interface does not provide some feature you need.

Start inviwo.
```
cd /home/inviwo-build/
./bin/inviwo
```
To setup a ENVISIoN visualisation take the following steps:
1. Open up the Inviwo python editor.
2. Click button to open a python file.
3. A dialog prompts you to pick a file. Scripts for visualisations are located in `/ENVISIoN/scripts`. Pick the script for what you want to visualise.
4. Configure the paths in the python file to correspond to where you have installed ENVISIoN, where your VASP output data is, and where you wish to save the resulting HDF5 file.

A visualisation should now start. The visualisation can now be configured using the Inviwo network editor.
<img src="/docs/READMEimages/inviwo_envision_startup.png" width="700">


## Building ENVISIoN as package
ENVISIoN can be build as an installable .deb package with the following steps:

Start by building Inviwo and installing ENVISIoN following the steps in [Installing ENVISIoN from source](#Installing-ENVISIoN-from-source)










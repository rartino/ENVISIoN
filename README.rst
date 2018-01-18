ENVISIoN: Electronic Structure Visualization Studio
===================================================

ENVISIoN is an open source tool/toolkit for electron visualization.

ENVISIoN is implemented using (a modified version of) the Inviwo visualization framework, developed at the Scientific Visualization Group at Linköping University (LiU).

The initial version was developed as part of the course TFYA75: Applied Physics - Bachelor Project, given at Linköping University, Sweden (LiU) spring term 2017. The title of the final report was: "Design och implementing av en interakiv visualisering av elektronstrukturdata". Authors: Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar. The project was supervised by Johan Jönsson (main supervisor), Rickard Armiento (expert and client), and Peter Steneteg (expert). The course examinator was Per Sandström.

The main part of ENVISoN is built using Python scripting in Inviwo. It provides a set of python 
routines that allows a user with just a few simple commands to:

- Read and parse output from electronic structure codes (presently VASP, and some support for Elk is implemented), storing the result in a structured HDF5 file.
- Generate interactive Inviwo visualization networks for
  tasks common when analyzing electronic structure calculations. 
  Presently there is (to varying degree) support for crystal structures, 
  ab-inito molecular dynamics, charge density, ELF, DOS/pDOS and 
  band structure visualization.

How to build and run ENVISIoN on Ubuntu Linux 17.10
---------------------------------------------------

Requirements: Ubuntu 17.10 with working graphics acceleration.

Create working directory
~~~~~~~~~~~~~~~~~~~~~~~~
::

  mkdir -p ~/ENVISIoN
  cd ~/ENVISIoN

Install dependencies
~~~~~~~~~~~~~~~~~~~~

Git::

  sudo apt-get install git 

Dependencies for Inviwo::

  sudo apt-get install build-essential
  sudo apt-get install cmake cmake-qt-gui cmake-curses-gui
  sudo apt-get install libpython3-dev libpython3-dbg 
  sudo apt-get install mesa-common-dev libglu1-mesa-dev
  sudo apt-get install libxcursor-dev libxinerama-dev libxrandr-dev

Qt5 (Using specifically Qt5.6.1 is highly recommended)::

  wget http://download.qt.io/official_releases/qt/5.6/5.6.1/qt-opensource-linux-x64-5.6.1.run
  chmod +x qt-opensource-linux-x64-5.6.1.run
  [ "$XDG_SESSION_TYPE" == "wayland" ] && xhost si:localuser:root # enable sudo with gui if on Wayland
  sudo ./qt-opensource-linux-x64-5.6.1.run
  [ "$XDG_SESSION_TYPE" == "wayland" ] && xhost -si:localuser:root 
  qtchooser -install Qt5.6.1 /opt/Qt5.6.1/5.6/gcc_64/bin/qmake
  export QT_SELECT=Qt5.6.1

Dependencies for ENVISIoN::

  sudo apt-get install doxygen python-sphinx-rtd-theme
  sudo apt-get install python3-h5py python3-regex

Download ENVISIoN
~~~~~~~~~~~~~~~~~
::

  git clone https://github.com/rartino/ENVISIoN 

Download and setup Inviwo
~~~~~~~~~~~~~~~~~
::

  git clone https://github.com/inviwo/inviwo.git inviwo.git

Prepare Inviwo repository with ENVISIoN patches *Note: The present version of ENVISIoN was developed against 
the commit #c345e1abbc1dee5ec810751c19bfb2af71f8f475.  
It seems to build correctly up to the later commit 5fa20ed7d63e9468f437ddefcb06440ffd7db04c.
ENVISIoN is not compatible with later versions due to API changes in inviwo.*
::

  cd inviwo.git
  git checkout 5fa20ed7d63e9468f437ddefcb06440ffd7db04c
  git submodule update --init --recursive
  patch -p1 < ../ENVISIoN/inviwo/patches/layerramprecision_swizzleswap.patch
  patch -p1 < ../ENVISIoN/inviwo/patches/hdf5_module_elseif.patch
  patch -p1 < ../ENVISIoN/inviwo/patches/pyvalueparser_matrix_intvectorproperty.patch
  patch -p1 < ../ENVISIoN/inviwo/patches/hdf5volumesource_dimensions_no_lower_bound.patch
  patch -p1 < ../ENVISIoN/inviwo/patches/makePyList_leak.patch 
  cd ..

Setup the Inviwo build directory::

  mkdir -p inviwo-envision
  cd inviwo-envision

Create Makefiles with cmake::

  cmake -G 'Unix Makefiles' -DCMAKE_PREFIX_PATH="/opt/Qt5.6.1/5.6/gcc_64/lib/cmake" -DIVW_DOXYGEN_PROJECT=OFF -DIVW_MODULE_PYTHON3=ON -DIVW_MODULE_PYTHON3QT=ON -DIVW_PROFILING=ON -DIVW_MODULE_BASECL=OFF -DIVW_MODULE_OPENCL=OFF -DIVW_MODULE_NIFTI=OFF -DIVW_MODULE_VECTORFIELDVISUALIZATION=ON -DIVW_MODULE_VECTORFIELDVISUALIZATIONGL=ON -DIVW_CMAKE_DEBUG=OFF -DIVW_EXTERNAL_MODULES="$(pwd -P)/../ENVISIoN/inviwo/modules" -DIVW_MODULE_CRYSTALVISUALIZATION=ON -DIVW_MODULE_GRAPH2D=ON -DIVW_MODULE_HDF5=ON -DIVW_MODULE_QTWIDGETS=ON -DCMAKE_CXX_FLAGS="-isystem /opt/Qt5.6.1/5.6/gcc_64/include/QtWidgets -isystem /opt/Qt5.6.1/5.6/gcc_64/include/" ../inviwo.git

Perform the build (set 8 = number of parallell build threads)::

  make -j8

Start inviwo and run the ENVISIoN example
-----------------------------------------

::

  bin/inviwo

- Open python editor under Python menu.
- In the Python Editor, open `~/ENVISIoN/ENVISIoN/examples/example.py`
- Edit the parameters to point to a VASP run.
- Press the python logo in the top left corner.

How to develop ENVISIoN and Inviwo
----------------------------------

Install development environment::
 
  sudo apt-get install gitg
  sudo apt-get install eclipse eclipse-pydev eclipse-cdt eclipse-cdt-qt

Create an Eclipse cmake project::

  mkdir -p ~/ENVISIoN/inviwo.eclipse
  cd  ~/ENVISIoN/inviwo.eclipse 
  cmake -G "Eclipse CDT4 - Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT=TRUE -DCMAKE_ECLIPSE_MAKE_ARGUMENTS=-j8 -DCMAKE_ECLIPSE_VERSION=3.8.1 -DCMAKE_PREFIX_PATH="/opt/Qt5.6.1/5.6/gcc_64/lib/cmake" -DIVW_DOXYGEN_PROJECT=OFF -DIVW_MODULE_PYTHON3=ON -DIVW_MODULE_PYTHON3QT=ON -DIVW_PROFILING=ON -DIVW_MODULE_BASECL=OFF -DIVW_MODULE_OPENCL=OFF -DIVW_MODULE_NIFTI=OFF -DIVW_MODULE_VECTORFIELDVISUALIZATION=ON -DIVW_MODULE_VECTORFIELDVISUALIZATIONGL=ON -DIVW_CMAKE_DEBUG=OFF -DIVW_EXTERNAL_MODULES="$(pwd -P)/../ENVISIoN/inviwo/modules" -DIVW_MODULE_CRYSTALVISUALIZATION=ON -DIVW_MODULE_GRAPH2D=ON -DIVW_MODULE_HDF5=ON -DIVW_MODULE_QTWIDGETS=ON -DCMAKE_CXX_FLAGS="-isystem /opt/Qt5.6.1/5.6/gcc_64/include/QtWidgets -isystem /opt/Qt5.6.1/5.6/gcc_64/include/" ../inviwo.git

*Note: Other options for CMAKE_BUILD_TYPE are: Release, RelWithDebInfo, MinSizeRel For better integration.*
  
Start eclipse::

  eclipse

- Close the welcome screen.
- Uncheck 'Project -> Build Automatically'
- File -> Import..., choose: Existing Projects into Workspace.
- For 'Select root directory' choose ENVISIoN/inviwo.eclipse in your home directory, eclipse should find the project.
- Click Finish.
- The project appear under inviwo-projects-Debug@inviwo.eclipse, in Project Explorer you'll find the source directory, i.e., inviwo.git, under '[Source directory]'. All modules, including the ENVISIoN ones show up under '[Subprojects]'.
- Click 'Build All' and inviwo should build.
- In the Project Explorer select bin/inviwo
- In the toolbar, click the drop-down arrow next to the green 'play' button and 'Run configurations...', select C/C++Application, and press the 'new' icon (a document with a star).
- The result should be a new Run configuration for bin/inviwo. Close the dialog.
- Press the green 'play' button in the toolbar, and Inviwo should run.  
  
- Select File->New project. Select PyDev -> PyDev Project.
- Set the name to ENVISIoN
- For Project contents, unclick 'Use default', and browse to ENVISIoN/ENVISIoN in your home directory.
- Select Python version 3.
- Next + Finish (no referenced projects)
- Feel free to Switch to the PyDev perspective. (Perspectives are how menues etc. are organized to fit the programming language you work with. You switch perspective manually with buttons in the top right corner.) 
- You can now browse with and work with the ENVISIoN python source files under the ENVISIoN project. (But work with the C++ modules under the Inviwo project.)


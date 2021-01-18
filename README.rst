===================================================
ENVISIoN: Electronic Structure Visualization Studio
===================================================

.. comment
   
   When editing this document, try to adhere to:
   
   - One sentence per line (this makes edit history in git the most clear).

.. sectnum::

ENVISIoN is an open source tool/toolkit for electron structure visualization developed in the Materials Design and Informatics unit in the `Theoretical Physics division <https://liu.se/en/organisation/liu/ifm/teofy>`__ at the `Department of Physics, Chemistry and Biology <https://liu.se/en/organisation/liu/ifm>`__ at `Linköping University (LiU). <https://liu.se/>`__
It is implemented using the `Inviwo visualization framework <https://inviwo.org/>`__, developed at the `Scientific Visualization Group <http://scivis.itn.liu.se/>`__ at LiU.

ENVISIoN provides a graphical user interface and a set of Python scripts that allow the user to visualise electronic structure quantities from ab-initio calculations. Presently only `VASP <https://www.vasp.at/>`__ output is well-supported.

ENVISIoN presently has the following features: visualization of crystal structure, electron density, electron localisation function, partial charge density, band structure, density of states, partial density of states, and pair correlation function.

ENVISIoN is licenced under `BSD 2-Clause “Simplified” License </LICENSE>`__.

| © 2017 - Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar.
| © 2018 - Anders Rehult, Andreas Kempe, Marian Brännvall, Viktor Bernholtz.
| © 2019 - Linda Le, Abdullatif Ismail, Anton Hjert, Lloyd Kizito and Jesper Ericsson.
| © 2017 – 2019 - Rickard Armiento, Johan Jönsson 

For more details about the contributions and devlopment history of ENVISIoN, see `Contributors`_.

.. contents::
   :depth: 3

Installation
============

Binary distribution
-------------------
ENVISIoN is packaged for some distributions (e.g. as ``.deb`` for Ubuntu Linux).

Packages called ``<something>-anaconda`` are recommended. 
These packages requires you to first install the `Anaconda <https://www.anaconda.com/>`__ distribution of Python 3.

After Anaconda is installed, download the appropriate packaged version of ENVISIoN from the `releases page <https://github.com/rartino/ENVISIoN/releases>`__ and install using your operating systems package manager.

You should now be able to start ENVISIoN using ``envision`` (and the ENVISIoN-adapted Inviwo using ``envision-inviwo``) in your terminal.


Build for Linux (Ubunty 20.04) from source
------------------------------------------

Install ENVISIoN files
~~~~~~~~~~~~~~~~~~~~~~ 

Install dependencies for ENVISIoN:

  apt install \
    python3 python3-pip \
    git \ 
    npm
  pip3 install numpy h5py pybind11 scipy regex

Download and install ENVISIoN:

  git clone https://github.com/rartino/ENVISIoN/
  cd ENVISIoN
  npm install

Building Inviwo
~~~~~~~~~~~~~~~

The first step is building and getting Inviwo to work. 

Install dependencies for building Inviwo:

  apt install \
        build-essential gcc-8 g++-8 cmake git freeglut3-dev xorg-dev \
        openexr zlib1g zlib1g-dev \
        qt5-default qttools5-dev qttools5-dev-tools \
        python3 python3-pip \
        libjpeg-dev libtiff-dev libqt5svg5-dev libtirpc-dev libhdf5-dev &&\
  pip3 install numpy h5py pybind11

Download and checkout the correct version of the Inviwo source

  git clone https://github.com/inviwo/inviwo --recurse-submodules
  cd inviwo
  git checkout v0.9.11
  git submodule update

Apply the ENVISIoN patches to Inviwo (paths may need to be changed based on location of the ENVISIoN directory):

  git apply \
    /ENVISIoN/inviwo/patches/deppack_fix.patch \
    /ENVISIoN/inviwo/patches/filesystem_env.patch \
    /ENVISIoN/inviwo/patches/ftl_fix.patch \
    /ENVISIoN/inviwo/patches/transferfunction_extras.patch \

Configure and build Inviwo (change /inviwo and /inviwo-build paths based on desired directories):
  mkdir inviwo-build
  cd inviwo-build/
  cmake -G "Unix Makefiles" \
    -DCMAKE_C_COMPILER="gcc-8" \
    -DCMAKE_CXX_COMPILER="g++-8" \
    -DBUILD_SHARED_LIBS=ON \
    -DIVW_USE_EXTERNAL_IMG=ON \
    -DIVW_EXTERNAL_MODULES="/ENVISIoN/inviwo/modules" \
    -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
    -DIVW_MODULE_GRAPH2D=ON \
    -DIVW_MODULE_HDF5=ON \
    -DIVW_USE_EXTERNAL_HDF5=ON \
    -DIVW_MODULE_PYTHON3=ON \
    -DIVW_MODULE_PYTHON3QT=ON \
    -DIVW_MODULE_QTWIDGETS=ON \
    -DIVW_PACKAGE_PROJECT=ON \
    -DIVW_PACKAGE_INSTALLER=ON \
    -S /inviwo -B ./
  make -j4

Test run Inviwo to make sure it built properly:
  ./inviwo-build/bin/inviwo

Run ENVISIoN
~~~~~~~~~~~~

ENVISIoN should now run with the following run in the ENVISIoN root directory:
  export INVIWO_HOME=/inviwo-build/bin
  npm start

Build for Linux from source using Anaconda
------------------------------------------

ENVISIoN requires Python 3 and quite specific versions of some dependencies.
You can choose to satisfy the dependences either by `Anaconda <https://www.anaconda.com/>`__ or by system packages.
In many cases the system-installable software may be too old, in which case using Anaconda is recommended.

**Note**: *Right now* the installation path using Anaconda dependencies does not work, as it gives a late-stage compilation error for Inviwo. This will shortly be fixed.

The rest of these instructions describe building ENVISIoN and Inviwo under ``~/ENVISIoN``.
This can be adapted as desired, but will require the corresponding changes of paths throughout the instructions.
Furthermore, for Anaconda installs, it is assumed the user installs anaconda in the default user directory of ``~/anaonda3``. If this is not the case, paths needs to be adjusted accordingly.

Furthermore, the package manager instructions apply to recent versions of Ubuntu. They need to be adapted for other Linux distributions.

Dependencies
~~~~~~~~~~~~

Dependencies using Anaconda
"""""""""""""""""""""""""""

Install system packages required by Anaconda. Follow the `instructions here <https://docs.anaconda.com/anaconda/install/linux/>`__, but specifically for Ubuntu Linux::

  sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 \
                   libxrandr2 libxss1 libxcursor1 libxcomposite1 \
	           libasound2 libxi6 libxtst6

Furthermore, even with Anaconda, there are some additional system packages needed for building Inviwo::

  sudo apt install build-essential gcc-8 g++-8 

Download `the latest Python 3 version of Anaconda <https://www.anaconda.com/distribution/#linux>`__ and install it.
		       
Create a conda environment with the needed dependencies::

  conda create --name envision
  conda activate envision
  conda install python=3
  conda install git pybind11 \
        numpy scipy matplotlib markdown regex wxpython \
	h5py hdf5 \
	qt=5 \
	libpng libtiff jpeg cmake \
        nodejs
	
  qtchooser -install anaconda ~/anaconda3/envs/envision/bin/qmake
  
**When doing new builds of ENVISIoN in a fresh environment, you need to remember to activate the envision conda environment**::

  conda activate envision

Dependencies without Anaconda
"""""""""""""""""""""""""""""
Inviwo dependencies via the package manager::

   sudo apt install \
     git build-essential \
     nodejs npm \
     libpng-dev libglu1-mesa-dev libxrandr-dev \
     libhdf5-dev libxinerama-dev libxcursor-dev \
     libtirpc-dev gcc-8 g++-8
     
ENVISIoN dependencies via package manager::

   sudo apt install \
     python3-h5py python3-regex
     
For cmake, version 3.12 or later required.
As of writing this the version supplied by Ubuntu apt-get is not compatible with Inviwo.
If the system provided cmake is too old, you need to uninstall it::

   sudo apt purge --auto-remove cmake

On Ubuntu you can get a newer version of cmake via snap::

  sudo snap install cmake --classic
 
Alternatively you can upgrade cmake manually from source:

   Execute this::

     mkdir ~/temp
     cd ~/temp
     wget https://cmake.org/files/v3.15/cmake-3.15.2-Linux-x86_64.sh 
     sudo mkdir /opt/cmake
     sudo sh cmake-$version.$build-Linux-x86_64.sh --prefix=/opt/cmake

   Add the installed binary link to /usr/local/bin/cmake by running this::

     sudo ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake

Verify that you have a working cmake of the correct version by running ``cmake -version``

For qt 5, you need at least qt 5.3, but higher versions are recommended.
If the system supplied version of qt is not new enough, you can follow these instructions::

   wget http://download.qt.io/official_releases/qt/5.12/5.12.2/qt-opensource-linux-x64-5.12.2.run
   chmod +x qt-opensource-linux-x64-5.12.2.run
   sudo ./qt-opensource-linux-x64-5.12.2.run
   qtchooser -install opt-qt5.12.2 /opt/Qt5.12.2/5.12.2/gcc_64/bin/qmake
  
Verify that Qt was installed in an appropriate version by running ``qmake -version``

Download ENVISIoN source
~~~~~~~~~~~~~~~~~~~~~~~~

Clone the ENVISON source code into ``~/ENVISIoN/ENVISIoN`` from the main repository::

  cd ~/ENVISIoN
  git clone https://github.com/rartino/ENVISIoN

Build Inviwo
~~~~~~~~~~~~

Clone the Inviwo source code from the main repository into ``~/ENVISIoN/inviwo``::

   cd ~/ENVISIoN
   git clone https://github.com/inviwo/inviwo.git
   cd inviwo
   git checkout v0.9.10
   git submodule update --init --recursive

This checks out version v0.9.10. Later versions may work but have not been tested.
   
.. comment
   old checkout was: 400de1a5af6a0400a314241b86982cfa2817dd9b
   
Apply ENVISIoN patches to inviwo::

   cd ~/ENVISIoN/inviwo
   git apply ~/ENVISIoN/ENVISIoN/inviwo/patches/2019/transferfunctionFix.patch
   git apply ~/ENVISIoN/ENVISIoN/inviwo/patches/2019/deb-package.patch
   git apply ~/ENVISIoN/ENVISIoN/inviwo/patches/2019/paneProperty2019.patch
   git apply ~/ENVISIoN/ENVISIoN/inviwo/patches/2019/sysmacro.patch
   git apply ~/ENVISIoN/ENVISIoN/inviwo/patches/2019/inviwo-v0.9.10-extlibs.patch
   
Setup a directory for building Inviwo::

   cd ~/ENVISIoN
   mkdir inviwo-build
   cd inviwo-build

Generate makefiles with cmake.

.. comment:

   This is how to activate Anaconda if you have not installed it into your init files::

     eval "$(~/anaconda3/bin/conda shell.bash hook)"

If using anaconda, generate the build files this way::

   export QT_SELECT=anaconda  
   eval `qtchooser --print-env`
   #export LIBRARY_PATH="$HOME/anaconda3/envs/envision/lib"
   #export CPATH="$HOME/anaconda3/envs/envision/include"
   /snap/bin/cmake -G "Unix Makefiles" \
     -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH" \
     -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH" \
     -DCMAKE_SYSTEM_PREFIX_PATH="$HOME/anaconda3/envs/envision" \
     -DCMAKE_SYSTEM_LIBRARY_PATH="${LIBRARY_PATH//:/;}" \
     -DCMAKE_C_COMPILER="gcc-8" \
     -DCMAKE_CXX_COMPILER="g++-8" \
     -DCMAKE_CXX_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DCMAKE_C_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DIVW_HDF5_USE_EXTERNAL:BOOL=ON \
     -DIVW_IMG_USE_EXTERNAL:BOOL=ON \
     -DIVW_EXTERNAL_MODULES="$HOME/ENVISIoN/ENVISIoN/inviwo/modules" \
     -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
     -DIVW_MODULE_FERMI=OFF \
     -DIVW_MODULE_GRAPH2D=ON \
     -DIVW_MODULE_PYTHON3=ON \
     -DIVW_MODULE_PYTHON3QT=ON \
     -DIVW_MODULE_QTWIDGETS=ON \
     -DIVW_MODULE_HDF5=ON \
     -DIVW_PACKAGE_PROJECT=ON \
     -DIVW_PACKAGE_INSTALLER=ON \
     ../inviwo

If not using anaconda, first select a suitable Qt (system or manually installed)::

   qtchooser -l
   export QT_SELECT=<qt version>

Where the first command list options to use in the second command.
   
Then generate the build files::
   
   eval `qtchooser --print-env`
   /snap/bin/cmake -G "Unix Makefiles" \
     -DCMAKE_PREFIX_PATH="$QTTOOLDIR/.." \
     -DCMAKE_C_COMPILER="gcc-8" -DCMAKE_CXX_COMPILER="g++-8" \
     -DIVW_HDF5_USE_EXTERNAL:BOOL=ON \
     -DIVW_IMG_USE_EXTERNAL:BOOL=ON \
     -DIVW_EXTERNAL_MODULES="$HOME/ENVISIoN/ENVISIoN/inviwo/modules" \
     -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
     -DIVW_MODULE_FERMI=OFF \
     -DIVW_MODULE_GRAPH2D=ON \
     -DIVW_MODULE_PYTHON3=ON \
     -DIVW_MODULE_PYTHON3QT=ON \
     -DIVW_MODULE_QTWIDGETS=ON \
     -DIVW_MODULE_HDF5=ON \
     -DIVW_PACKAGE_PROJECT=ON \
     -DIVW_PACKAGE_INSTALLER=ON \
     ../inviwo

Now build inviwo::

   make -j5

Once complete, verify that build worked by running ``./bin/inviwo``. The Inviwo GUI applicaiton should start.

Configure ENVISIoN
~~~~~~~~~~~~~~~~~~

Install required node modules for the ENVISIoN GUI::

   cd ~/ENVISIoN/ENVISIoN
   npm install

Depending on whether you changed the path to where you built inviwo, you may need to set the environment variable ``INVIWO_HOME`` to your ``inviwo-build`` directory.

Finally, insert the ENVISIoN bin directory into your path::

  export PATH="$HOME/ENVISIoN/ENVISIoN/bin:$PATH"

Package ENVISIoN for distribution
=================================

Installation packages for Linux
-------------------------------

ENVISIoN can be built into an installable .deb package using the Dockerfile located in `packaging/docker/`. Generate packages by building the docker image and running it.

Build the docker image to the required build step:
  docker build -f packaging/docker/Dockerfile --target envision_packager -t envision_packager .

Run the docker image. It will copy the built packages to the directory it is run from. Change `$(pwd)` to something else to selet another directory:
  docker run -it --rm -v $(pwd):/package_output envision_packager


Setup a development environment
===============================

Eclipse
-------

Install needed files for eclipse::
  
  sudo apt-get install gitg
  sudo apt-get install eclipse eclipse-pydev eclipse-cdt eclipse-cdt-qt

Create an Eclipse cmake project::

  eval `qtchooser --print-env`
  mkdir -p ~/ENVISIoN/inviwo.eclipse
  cd ~/ENVISIoN/inviwo.eclipse
  cmake -G "Eclipse CDT4 - Unix Makefiles" \
      \
     -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH" \
     -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH" \
     -DCMAKE_SYSTEM_PREFIX_PATH="$HOME/anaconda3/envs/envision" \
     -DCMAKE_SYSTEM_LIBRARY_PATH="${LIBRARY_PATH//:/;}" \
     -DCMAKE_C_COMPILER="gcc-8" \
     -DCMAKE_CXX_COMPILER="g++-8" \
     -DCMAKE_CXX_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DCMAKE_C_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DIVW_HDF5_USE_EXTERNAL:BOOL=ON \
     -DIVW_IMG_USE_EXTERNAL:BOOL=ON \
     -DIVW_EXTERNAL_MODULES="$HOME/ENVISIoN/ENVISIoN/inviwo/modules" \
     -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
     -DIVW_MODULE_FERMI=OFF \
     -DIVW_MODULE_GRAPH2D=ON \
     -DIVW_MODULE_PYTHON3=ON \
     -DIVW_MODULE_PYTHON3QT=ON \
     -DIVW_MODULE_QTWIDGETS=ON \
     -DIVW_MODULE_HDF5=ON \
     -DIVW_PACKAGE_PROJECT=ON \
     -DIVW_PACKAGE_INSTALLER=ON \
     \
     -DCMAKE_BUILD_TYPE=Debug \
     -DCMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT=TRUE \
     -DCMAKE_ECLIPSE_MAKE_ARGUMENTS=-j5 \
     -DCMAKE_ECLIPSE_VERSION=3.8.1 \
     -DIVW_PROFILING=ON

Where the upper section is the same for a regular build (here using an Anaconda setup, but it can be replaced with a cmake run for using system dependencies instead).
The lower section are eclipse-development-specific settings.

Note: other options for CMAKE_BUILD_TYPE are: Release, RelWithDebInfo, MinSizeRel.

Now start eclipse::

  eclipse

Do the following:

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

Visual Studio Code
------------------

Another popular development environment is `Visual Studio Code <https://code.visualstudio.com/download>`__.

Starting ENVISIoN
=================

Starting ENVISIoN in GUI mode
-----------------------------

Once properly installed, the ENVISIoN GUI can be started this way::

  envision

You should now see the main window from where ENVISIoN can be controlled.

Using ENVISIoN from inside the Inviwo GUI 
------------------------------------------

ENVISIoN is implemented as python 3 scripts that do visualisations in Inviwo.
For development work or to access more visualization features, the ENVISIoN scripts can be run directly inside the main Inviwo GUI.
This is, however, less user-firendly than the dedicated ENVISIoN GUI.

Start the inviwo GUI::

   envision-inviwo
  
To setup a ENVISIoN visualisation take the following steps:

1. Open up the Inviwo python editor.
2. Click button to open a python file.
3. A dialog prompts you to pick a file.
   Scripts for visualisations are located in the directory ``scripts`` in your ENVISIoN directory.
   Pick the script for what you want to visualise.
4. Configure the paths in the python file to correspond to where you have installed ENVISIoN, where your VASP output data is, and where you wish to save the resulting HDF5 file.

A visualisation should now start.
The visualisation can now be configured using the Inviwo network editor.

Using ENVISIoN
==============

For more information on how to use the ENVISIoN application, see the `User's guide <docs/users_guide/users_guide.rst>`__.


Contributors
============

2017
----

The initial version of ENVISIoN was developed the spring term 2017 as part of the course *TFYA75: Applied Physics - Bachelor Project*, given at Linköping University, Sweden (LiU) by Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar.
The project was supervised by Rickard Armiento (requisitioner and expert), Johan Jönsson (head supervisor), and Peter Steneteg (expert).
The course examinator was Per Sandström.

2018
----

ENVISIoN was further developed during the spring term of 2018 as part of the same course by Anders Rehult, Andreas Kempe, Marian Brännvall, and Viktor Bernholtz.
The project was supervised by Rickard Armiento (requisitioner and expert), Johan Jönsson (head supervisor).
The course examinator was Per Sandström.

Work on implementing visualization of partial electronic charge was done as a project work by Elvis Jacobson during the fall term of 2018.

2019
----

ENVISIoN was further developed during the spring term of 2019 as part of the same course by: Linda Le, Abdullatif Ismail, Anton Hjert, Lloyd Kizito and Jesper Ericsson.
The project was supervised by Rickard Armiento (requisitioner and expert), Johan Jönsson (head supervisor), and Peter Steneteg (expert). The course examiner was Per Sandström.
Requisitioner and co-supervisor: 
Visualization expert: Peter Steneteg; and 

During summer 2019 the development was continued by Jesper Ericsson, primarily creating the Electron-based GUI.






.. comment

   This is a saved legacy recepie from when the idea was to use a complete conda
   environment also for a large amount of system dependencies. However, this failed
   on not being able to link against system libGL.so or - if installing a mesa libGL -
   libglapi.so which was not provided in conda. 

   conda install git numpy scipy h5py regex pybind11 wxpython \
        matplotlib markdown qt=5 libpng libtiff jpeg cmake gcc_linux-64=7 gxx_linux-64=7 \
        nodejs \
	libx11-devel-cos6-x86_64 libxrandr-devel-cos6-x86_64 libxinerama-devel-cos6-x86_64 \
	libxcursor-devel-cos6-x86_64 libxrender-devel-cos6-x86_64 \
	xorg-x11-proto-devel-cos6-x86_64 \
        libxi-devel-cos6-x86_64 libxext-devel-cos6-x86_64 libglu \
	hdf5  \
	libx11-devel-cos6-x86_64 libxcursor-cos6-x86_64 \
	libxfixes-devel-cos6-x86_64 \
	libxdamage-cos6-x86_64 libxxf86vm-cos6-x86_64 libxau-cos6-x86_64 \
        libselinux-cos6-x86_64
	
        #mesa-libgl-devel-cos6-x86_64 #pyopengl libselinux   

   export QT_SELECT=anaconda  
   eval `qtchooser --print-env`
   mkdir -p "$HOME/anaconda3/envs/envision/ext-lib"
   ln -s /usr/lib/x86_64-linux-gnu/libGL.so "$HOME/anaconda3/envs/envision/ext-lib"
   ln -s /lib/x86_64-linux-gnu/libc.so.6 "$HOME/anaconda3/envs/envision/ext-lib"
   export LIBRARY_PATH="$HOME/anaconda3/envs/envision/ext-lib:$HOME/anaconda3/envs/envision/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64:$HOME/anaconda3/envs/envision/lib"
   export CPATH="$HOME/anaconda3/envs/envision/x86_64-conda_cos6-linux-gnu/sysroot/usr/include/:$HOME/anaconda3/envs/envision/include"
   /snap/bin/cmake -G "Unix Makefiles" \
     -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH -Wl,-rpath-link,/usr/lib/x86_64-linux-gnu/" \
     -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-rpath-link,$LIBRARY_PATH -Wl,-rpath-link,/usr/lib/x86_64-linux-gnu/" \
     -DCMAKE_SYSTEM_PREFIX_PATH="$HOME/anaconda3/envs/envision" \
     -DCMAKE_SYSTEM_LIBRARY_PATH="${LIBRARY_PATH//:/;}" \
     -DCMAKE_C_COMPILER="x86_64-conda_cos6-linux-gnu-gcc" \
     -DCMAKE_CXX_COMPILER="x86_64-conda_cos6-linux-gnu-g++" \
     -DCMAKE_CXX_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DCMAKE_C_FLAGS="-isystem '$HOME/anaconda3/envs/envision/include'" \
     -DIVW_HDF5_USE_EXTERNAL:BOOL=ON \
     -DIVW_IMG_USE_EXTERNAL:BOOL=ON \
     -DIVW_EXTERNAL_MODULES="$HOME/ENVISIoN/ENVISIoN/inviwo/modules" \
     -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
     -DIVW_MODULE_FERMI=OFF \
     -DIVW_MODULE_GRAPH2D=ON \
     -DIVW_MODULE_PYTHON3=ON \
     -DIVW_MODULE_PYTHON3QT=ON \
     -DIVW_MODULE_QTWIDGETS=ON \
     -DIVW_MODULE_HDF5=ON \
     -DIVW_PACKAGE_PROJECT=ON \
     -DIVW_PACKAGE_INSTALLER=ON \
     ../inviwo

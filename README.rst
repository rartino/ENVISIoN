ENVISIoN: Electronic Structure Visualization Studio
===================================================
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

Prepare Inviwo using the ENVISIoN install script on Ubuntu 18.04 LTS
--------------------------------------------------------------------


These instructions show how to build Inviwo and ENVISIoN on Ubuntu 18.04 LTS. ENVISIoN provides an install script for Ubuntu 18.04 LTS. Executing the installation script will install all required dependencies, clone Inviwo from Github and configure the Inviwo build.
The script should *NOT* be run as root, but as your own user and it will ask for your password when it needs root rights. It is possible that the script will ask for other user input during the process, if that’s the case, just accept the default. This guide will assume that both ENVISIoN and Inviwo will be placed directly under the home folder.

::
  cd ~/ENVISIoN/scripts
  ./install.sh /home/$USER/ENVISIoN /home/$USER/inviwo

Once the installation script has run, it prints build instructions. Follow the instructions and start the build. The instructions will tell you to cd to the build directory and execute make.

An easy way to modify the build settings, if needed, is to install the cmake curses gui and run it in the build directory.

To install the cmake gui:

::
  sudo apt install cmake-curses-gui

Running cmake in the build directory:

::
  cd ~/inviwo/build
  ccmake .

When in the GUI, press c to apply the current configuration, g to generate build files and q to quit. If settings have changed, it is possible that you will need to press c more than once before the g option becomes available.

After having generated the build files, the project can now be rebuilt with the new settings by executing *make* like earlier.

Prepare Inviwo for build
------------------------

To be able to install Inviwo, all required dependencies needs to installed:
- gcc
- hdf5
- cmake
- qt
- python3
- numpy
- h5py
- regex
- wxPython
- pybind11

Make sure to install the latest version of all the softwares mentioned above. Clone the Inviwo repository into the home folder and make it your working directory. Clone the Inviwo repository be executing the command below.

::
  git clone https://github.com/inviwo/inviwo.git

ENVISIoN isn’t compatible with the newest version of Inviwo due to a reconstruction in the Inviwo file system on April 15, 2019. To make ENVISIoN compatible with Inviwo that just got cloned, a checkout of a compatible version is needed.

::
  git checkout d20199dfd37c80559ce687243d296f6ce3e41c71

Some minor alterations has been made on the Inviwo source code by the ENVISIoN project group that need to be patched.

::
  git apply < "~/ENVISIoN/inviwo/patches/2019/envisionTransferFuncFix2019.patch"
  git apply < "~/ENVISIoN/inviwo/patches/2019/paneProperty2019.patch"

The only remaining change in the Inviwo repository is an update of its submodules.

::
  git submodule init

Create a build directory in the home folder and configure the ENVISIoN module and project path using cmake. Execute the command below when standing in the build directory.

::
  cmake ../inviwo -DIVW_EXTERNAL_PROJECTS="~/ENVISIoN/inviwo/app" \
        -DIVW_EXTERNAL_MODULES="$~/ENVISIoN/inviwo/modules" \
        -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
        -DIVW_MODULE_FERMI=OFF \
        -DIVW_MODULE_GRAPH2D=ON \
        -DIVW_MODULE_PYTHON3=ON \
        -DIVW_MODULE_PYTHON3QT=ON \
        -DIVW_MODULE_QTWIDGETS=ON \
        -DIVW_MODULE_HDF5=ON

Inviwo is now ready to be installed with the ENVISIoN modules added. Add the -j extension to use multiple cores while installing.

::
  make -j5

Start ENVISIoN
--------------
After the Inviwo build is done, an application named *inviwo_envisionminimum* will be available in the bin files in the build directory. The commands in this section are only compatible with Ubuntu 18.04 LTS and other UNIX based operating systems. To make the application start the graphical user interface, it needs the path to the interface source files located in the same directory. The file containing these files can be copied from *∼/ENVISIoN/scripts* and is named *ENVISIoNimport.py.*
Execute the command below to copy the file to the correct directory.

::
  cp ~/ENVISIoN/scripts/ENVISIoNimport.py ~/build/bin/ENVISIoNimport.py

The application can now be started by standing in the build directory and executing the command below.

::
  ./bin/inviwo_envisionminimum

Start Inviwo and run ENVISIoN scripts
--------------------------------------

If the user wishes to run Inviwo with its own graphical user interface, it’s possible and still have access to the visualizations provided by ENVISIoN. These visualizations are stored in the form of Python scripts that can be compiled through the Inviwo user interface.
To run Inviwo in an UNIX environment, execute the commands below.

::
  cd ~/build
  ./bin/inviwo

When the Inviwo interface has opened, follow the instructions given in figure 1 and in the list below to run a visualization script.

Locate and press the Python menu in the Inviwo bar.

1. Locate and press the Python menu in the Inviwo bar.
2. Open the Python editor by pressing it.
3. In the Python editor, click Open Script.
4. Select one of the scripts. The ENVISIoN scripts can be located in ∼/ENVISIoN/scripts.
5. Click open.
6. Click the button in the top left corner to run.

<img src="/docs/READMEimages/figure1.png" width="600">


Graphical user interface
------------------------

The purpose of the graphical user interface is to simplify the usage of ENVISIoN.

Start-up
~~~~~~~~~

When the user run the application a window opens, see figure 2. After ENVISIoN has been opened, two possible menu-choices appear, “Parser” and “Visualization”.

<img src="/docs/READMEimages/figure2.png" width="400">

Parser menu
~~~~~~~~~~~~

The parser menu is localized on top in the interface. To access its content, press the fold out button to expand the menu. The result will be that of figure 3, depending on the system running the software.

For quick step-by-step guide, scroll down to last segment of this subsection.

<img src="/docs/READMEimages/figure3.png" width="400">

In the blue box, labeled “1”, the path to the directory of VASP-files to parse is selected. There are two options, either the path can be entered as a string in the text field or the “..or select dir”-button can be pressed. This button will reveal the file explorer and allow to select the desired folder.

In the red box, labeled “2”, the path to the desired saving directory for the new hdf5-files is selected. This path-selection has the same two options as the previous.

In the yellow box, labeled “3”, the path to an existing hdf5-file can be selected. Here, there are two options as well, which are similar to those above. The difference is that the button will open a file explorer where an hdf5-file shall be selected.

In the green box, labeled “4”, the type of the parsing for certain visualizations can be picked. If one type of visualization is desired, there can be of advantage to pick that in the drop-down list to enhance performance of the parser. If not changed or if “All” is selected, the parser will run all possible types of parsing. The available choices for types are:

- All
- Bandstructure
- Charge
- DoS - Density of States
- ELF - Electron Localization Function • Fermi Energy
- MD - Molecular Dynamics
- Parchg - Partial Charge
- PCF - Pair Correlation Function
- Unitcell

In the brown box, labeled “5”, if a new hdf5-file is to created, the name of the new file is entered here without file extension.

In the purple box, labeled “6”, is the execution-button of the parser. When pressing this button the parser tries to run. Afterwards, a message box will appear on the screen with the status of the parsing. If the parsing was successful the message box will show for which data the parsing was done. If it failed, the message box will tell where it failed. If no message box appear, then something went wrong that wasn’t detected, an exception that wasn’t caught.

Quick Step-by-Step Guide
~~~~~~~~~~~~~~~~~~~~~~~~

For new *.hdf5 file:
1. Enter path to directory in “1”.
2. Enter path to directory in “2”.
3. Select type in “4”.
4. Enter new file name in “5”.
5. Press “Parse” in “6”.
6. Message whether the parsing was successful or not will appear.

For existing .hdf5 file:

1. Enter path to directory in “1”.
2. Enter path to file in “3”.
3. Select type in “4”.
4. Press ’Parse’ in “6”.
5. Message weather the parsing was successful or not will appear.

Visualization menu
~~~~~~~~~~~~~~~~~~~

Common controls - Charge Density, ELF, and Partial Charge Density
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Because of the strong similarity between these three menues the interface share many elements. The common elements will be described here.

When opening any of the visualization main menues four sub-menues will be visible. *Volume Rendering*, *Volume Slice*, *Atom Rendering* and *Background*. All those control different aspects of the visualization.

Volume Rendering menu
**********************

<img src="/docs/READMEimages/figure4.png" width="300">

(1) Drop-down menu to choose volume shading mode. Affects how the volume is lighted.
(2) Toggle full transparency for volume densities lower than the lowest transfer function point.
(3) Edit existing transfer function points by editing text fields or picking color. Remove point by pressing “-” button.
(4) Add new transfer function point with specified value, alpha, and color by pressing “+” button.
(5) Click button to show volume density distribution histogram. Histogram will open in a new window.
(6) Click to save or load active transfer function.

Volume Slice menu
*****************

<img src="/docs/READMEimages/figure5.png" width="300">

(1) Text fields specify (x, y, z)-components of the normal vector of slice plane.
(2) Slider controls the height of the slice plane.
(3) Expandable menu to control the background of the slice image.

Atom Rendering menu
*******************

<img src="/docs/READMEimages/figure6.png" width="300">

(1) Sliders to choose the radius of each atom type.

Background menu
***************

<img src="/docs/READMEimages/figure7.png" width="450">

(1) Drop-down menu to choose the background pattern style.
(2) Select the two colors of the background. Either use the color picker on the left, or specify a RGBA-color via the text fields
(3) Button to swap positions of the colors.
(4) Drop-down menu to choose the blend mode of the background.

Charge Density
"""""""""""""""

<img src="/docs/READMEimages/figure8.png" width="300">

(1) Drop-down menu to select which band to visualize. Each band has its own volume data.
(2) Toggle the atom sphere rendering.
(3) Toggle the volume slice visualization.
(4) Expand the Volume Rendering menu.
(5) Expand the Atom Rendering menu.
(6) Expand the Background menu.
(7) Expand the Volume Slice menu.

ELF - Electron Localization Function
"""""""""""""""""""""""""""""""""""""

<img src="/docs/READMEimages/figure9.png" width="450">

(1) Drop-down menu to select which band to visualize. Each band has its own volume data.
(2) Toggle the atom sphere rendering.
(3) Toggle the volume slice visualization.
(4) Expand the Volume Rendering menu.
(5) Expand the Atom Rendering menu.
(6) Expand the Background menu.
(7) Expand the Volume Slice menu.

Partial charge density
"""""""""""""""""""""""

<img src="/docs/READMEimages/figure10.png" width="450">

(1) Manage selected bands and modes. Band selections and modes can be changed. Select “None” to remove band from visualization.
(2) Add new band selection with selected mode. Select any other opetion than ”None” to add new band to visualization.
(3) Toggle the atom sphere rendering.
(4) Toggle the volume slice visualization.
(5) Expand the Volume Rendering menu.
(6) Expand the Atom Rendering menu.
(7) Expand the Background menu.
(8) Expand the Volume Slice menu.

Bandstructure
""""""""""""""

When expanding the bandstructure visualization menu the visualization starts and a control panel appears. This menu is shown in figure 11.

<img src="/docs/READMEimages/figure11.png" width="600">

The bandstructure visualization menu contains a number of possibilities to control parameters.

Range and Scale:
*****************

In the first (blue) box, controls for scaling and changing the visible interval appears. The range boxes sets minimum and maximum values for the axes to show. The scale box sets the scaling for the entire graph with maximum one and minimum at one over a hundred.

Help line:
************

The help line, the blue line in the graph, is controlled by the red box in the graphical interface. By checking and unchecking the box, the help line is enabled and disabled. When the line is enabled, it is possible to move around to check which X-values corresponds to what part of the curve in the graph.

Grid:
*******

When grid is checked (yellow box) the visible mesh in figure 11 appears. The frequency of the grid lines is in direct relations to number of labels, covered in the next paragraph. The thickness of the lines is controlled from the text entry below the checkbox for the grid.

Labels:
*********

In the green box, the option of labels concerns if labels should be visible on the axes or not and the number of labels appearing along the axes. There is one option for each axis to show or hide the labels. The text entry is for number of labels apart from lowest value.

List of Y:
************

Below the label “List of Y” in the brown box are controls for choosing lines to show and a list of all possible choices.The drop down list is not a control, it’s a list of the possible bands to show. The tick box for “Enable all Y” enables all Y-values to be visualized or not. When enabled, the option to visualize some or one of the bands is disabled. The tick box for enabling y selection reveals a hidden text entry. Here it’s possible to choose one or more band to visualize. The options of how to choose the lines are; “n”, “n:N”, “n,N” or some combination of these, where n and N are arbitrary integers corresponding to list indices.

DoS - Density of States
""""""""""""""""""""""""

When expanding the density of states visualization menu the visualization starts and a control panel appears. The menu is shown in figure 12.

<img src="/docs/READMEimages/figure12.png" width="600">

Range and Scale:
********************

In the first, controls for scaling and changing the visible interval appears. The range boxes sets minimum and maximum values for the axes to show. The scale box sets the scaling for the entire graph with maximum one and minimum at one over a hundred.

Help line:
************

The help line is controlled by the red box in the graphical interface. By checking and unchecking the box, the help line is enabled and disabled. When the line is enabled, it is possible to move around to check which X-values corresponds to what part of the curve in the graph.

Grid:
************

When grid is checked the visible mesh in figure 11 appears. The frequency of the grid lines is in direct relations to number of labels, covered in the next paragraph. The thickness of the lines is controlled from the text entry below the checkbox for the grid.

Labels:
************

The option of labels concerns if labels should be visible on the axes or not and the number of labels appearing along the axes. There is one option for each axis to show or hide the labels. The text entry is for number of labels apart from lowest value.

List of Y:
************

Below the label ’List of Y’ are controls for choosing lines to show and a list of all possible choices. Here, the drop down list is a control, which can select what line to show in the graph. The tick box for “Enable all Y” enables all Y-values to be visualized or not. When enabled, the option to visualize some or one of the bands is disabled. The tick box for enabling y selection reveals a hidden text entry. Here it’s possible to choose one or more band to visualize. The options of how to choose the lines are; “n”, “n:N”, “n,N” or some combination of these, where n and N are arbitrary integers corresponding to list indices.

PCF - Pair Correlation Function
""""""""""""""""""""""""""""""""

When expanding the PCF visualization menu the visualization starts and a control panel appears. In figure 13, this menu is visible.

<img src="/docs/READMEimages/figure13.png" width="600">

Range and Scale:
*****************

In the first, controls for scaling and changing the visible interval appears. The range boxes sets minimum and maximum values for the axes to show. The scale box sets the scaling for the entire graph with maximum one and minimum at one over a hundred.

Help line:
************

The help line is controlled by the red box in the graphical interface. By checking and unchecking the box, the help line is enabled and disabled. When the line is enabled, it is possible to move around the line to check which X-values corresponds to what part of the curve in the graph.

Grid:
*******

When grid is checked the visible mesh in figure 11 appears. The frequency of the grid lines is in direct relations to number of labels, covered in the next paragraph. The thickness of the lines is controlled from the text entry below the checkbox for the grid.

Labels:
********

The option of labels concerns if labels should be visible on the axes or not and the number of labels appearing along the axes. There is one option for each axis to show or hide the labels. The text entry is for number of labels apart from lowest value.

List of Y:
***********

Below the label “List of Y” are controls for choosing lines to show and a list of all possible choices. Here, the drop down list is a control, which can select what line to show in the graph. The tick box for “Enable all Y” enables all Y-values to be visualized or not. When enabled, the option to visualize some or one of the bands is disabled. The tick box for enabling y selection reveals a hidden text entry. Here it’s possible to choose one or several bands to visualize. The options of how to choose the lines are; “n”, “n:N”, “n,N” or some combination of these, where n and N are arbitrary integers corresponding to list indices.

Common errors during installation
-----------------------------------

Qt
~~~

Inviwo uses the graphics library Qt which isn’t always installed properly. These instructions show how to download and install the latest version of Qt on Ubuntu 10.04 LTS. That is, in the moment of writing this user guide, version 5.12.3.

To download the installation file into the */Downloads* directory, simply execute the commands below.

::
  cd ~/Downloads
  wget http://download.qt.io/official_releases/qt/5.12/5.12.3/qt-opensource-linux-x64-5.12.3.run

When the installation file has finished downloading, the user won’t have permission to run the file. To change permissions and run the file by executing the commands below and enter your superuser password immediately after.

::
  chmod +x qt-opensource-linux-x64-5.12.3.run
  sudo ./qt-opensource-linux-x64-5.12.3.run

An Qt installer is now shown on the screen. Notice that the manual installation will force a installation of the Qt editor as shown in step 6. The entire installation will occupy approximately 5.12 GB. Follow the instructions in figure 14 to complete the installation.

After the installation is done, the path to Qt needs to be added to the system. Add the necessary paths by executing the commands below.

::
  cd /usr/lib/x86_64-linux-gnu/qtchooser
  sudo echo "/opt/Qt5.12.3/5.12.3/gcc_64/bin" | sudo tee -a default.conf
  sudo echo "/opt/Qt5.12.3/5.12.3/gcc_64/lib" | sudo tee -a default.conf

The system is now ready for an Inviwo installation.

<img src="/docs/READMEimages/figure14.png" width="600">

Build instructions from 2017 (stored here mostly for reference)
===================================================

How to build and run ENVISIoN on Ubuntu 18.04
---------------------------------------------

Requirements: Ubuntu 18.04 with working graphics acceleration.

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

  sudo apt install build-essential qtchooser cmake cmake-qt-gui \
    cmake-curses-gui \
    libpython3-dev libpython3-dbg \
    mesa-common-dev libglu1-mesa-dev \
    libxcursor-dev libxinerama-dev libxrandr-dev \
    qtchooser libzma-dev python3-distutils gcc-8 g++-8 gfortran-8

Qt5 (Using specifically Qt5.6.1 is highly recommended)::

  wget http://download.qt.io/official_releases/qt/5.6/5.6.1/qt-opensource-linux-x64-5.6.1.run
  chmod +x qt-opensource-linux-x64-5.6.1.run
  [ "$XDG_SESSION_TYPE" == "wayland" ] && xhost si:localuser:root # enable sudo with gui if on Wayland
  sudo ./qt-opensource-linux-x64-5.6.1.run
  [ "$XDG_SESSION_TYPE" == "wayland" ] && xhost -si:localuser:root
  qtchooser -install Qt5.6.1 /opt/Qt5.6.1/5.6/gcc_64/bin/qmake
  export QT_SELECT=Qt5.6.1

Dependencies for ENVISIoN::

  sudo apt install doxygen python-sphinx-rtd-theme \
    python3-h5py python3-regex python3-numpy python3-matplotlib

Download ENVISIoN
~~~~~~~~~~~~~~~~~
::

  git clone https://github.com/rartino/ENVISIoN

Download and setup Inviwo
~~~~~~~~~~~~~~~~~
::

  git clone --recurse-submodules https://github.com/inviwo/inviwo.git inviwo.git

Prepare Inviwo repository with ENVISIoN patches
::

  cd inviwo.git
  patch -p1 < ../ENVISIoN/inviwo/patches/2018/2018-compatability.patch
  cd ..

Setup the Inviwo build directory::

  mkdir -p inviwo-envision
  cd inviwo-envision

Create Makefiles with cmake::

  export CC=/usr/local/bin/gcc-8
  export CXX=/usr/local/bin/g++-8
  export FC=/usr/local/bin/gfortran-8

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

Build instructions from 2017 (stored here mostly for reference)
=========================================================

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
  sudo apt-get install python3-h5py python3-regex python3-numpy python3-matplotlib

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

  cmake -G 'Unix Makefiles' -DCMAKE_PREFIX_PATH="/opt/Qt5.6.1/5.6/gcc_64/lib/cmake" -DIVW_EXTERNAL_MODULES="$(pwd -P)/../ENVISIoN/inviwo/modules" DCMAKE_CXX_FLAGS="-isystem /opt/Qt5.6.1/5.6/gcc_64/include/QtWidgets -isystem /opt/Qt5.6.1/5.6/gcc_64/include/" ../inviwo.git

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

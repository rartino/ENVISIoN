#!/usr/bin/env sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 envision_path inviwo_install_path"
    echo "Example: $0 /home/user/ENVISIoN /home/user/inviwo"
    exit 0
fi

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    sudo apt install git \
                     build-essential \
                     libpng-dev \
                     libhdf5-dev \
                     qtbase5-dev \
                     qttools5-dev \
                     gcc \
                     cmake \
                     python3-dev \
                     python3-numpy \
                     python3-h5py \
                     python3-regex \
                     libglu1-mesa-dev \
                     libxrandr-dev \
                     libxinerama-dev \
                     libxcursor-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Install and update homebrew.
    #/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)
    # Install packages needed for Inviwo and ENVISIoN.
    brew install libpng \
                 python@3 \
                 gcc \
                 hdf5 \
                 git \
                 cmake \
                 qt
    # Install Python packages
    pip3 install numpy \
                 h5py \
                 regex
elif [[ "$OSTYPE" == "win32" ]]; then
    echo "Not implemented for windows yet!"
else
    echo "This installation script doesn't support your operating system"
    echo "Exiting..."
    exit 1
fi

# Get Inviwo repository and enter directory.
git clone https://github.com/inviwo/inviwo.git "$2"
if [[ "$OSTYPE" == "win32" ]]; then
    echo "Not implemented for windows yet!"
else
    cd "$2"
fi

# Checkout correct version.
git checkout v.0.9.9.1

# Apply 2019 patch.
<<<<<<< HEAD
git apply < "$1/inviwo/patches/2019/patch2019.patch"
=======
git apply < "$1/inviwo/patches/2019/paneProperty2019.patch"
>>>>>>> 2c6df37b7212d0705c6b357f3028e4609fe249ec

# Init and update submodules.
git submodule init

# Create and enter a build directory.
if [[ "$OSTYPE" == "win32" ]]; then
    echo "Not implemented for windows yet!"
else
    mkdir build
    cd build
fi

# Enable relevant ENVISIoN-modules.
cmake .. -DIVW_EXTERNAL_PROJECTS="$1/inviwo/app" \
         -DIVW_EXTERNAL_MODULES="$1/inviwo/modules" \
         -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
         -DIVW_MODULE_FERMI=OFF \
         -DIVW_MODULE_GRAPH2D=ON \
         -DIVW_MODULE_PYTHON3=ON \
         -DIVW_MODULE_PYTHON3QT=ON \
         -DIVW_MODULE_QTWIDGETS=ON \
         -DIVW_MODULE_HDF5=ON

# build the application.
make -j5

echo ""
echo ""
echo ""
echo "#####################################################################################"
echo "Inviwo has now been build with ENVISIoN."
echo "You can find and run the Inviwo and ENVISIoN application in bin directory:"
echo "$2/build/bin"
echo "######################################################################################"

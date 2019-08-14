#!/usr/bin/env sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 envision_path inviwo_install_path"
    echo "Example: $0 /home/user/ENVISIoN /home/user/inviwo"
    exit 0
fi

# Install all necessary dependencies.
sudo apt install git \
                 build-essential \
                 libpng-dev \
                 libhdf5-dev \
                 qt5-default \
                 qtbase5-dev \
                 qttools5-dev \
                 gcc \
                 cmake \
                 python3-dev \
                 python3-pip \
                 python-wxgtk4.0 \
                 libglu1-mesa-dev \
                 libxrandr-dev \
                 libxinerama-dev \
                 libxcursor-dev

pip3 install numpy
pip3 install h5py
pip3 install regex
pip3 install matplotlib
pip3 install pybind11

# Get Inviwo repository and enter directory.
git clone https://github.com/inviwo/inviwo.git "$2"
cd "$2"

# Checkout correct version.
git checkout 400de1a5af6a0400a314241b86982cfa2817dd9b

# Apply 2019 patch.
git apply < "$1/inviwo/patches/2019/envisionTransferFuncFix2019.patch"
git apply < "$1/inviwo/patches/2019/deb-package.patch"

# Init and update submodules.
git submodule init
git submodule update --init --recursive
git submodule update

# Create and enter a build directory.
cd ..
mkdir build
cd build

# Enable relevant ENVISIoN-modules.
cmake "$2" -DIVW_EXTERNAL_PROJECTS="$1/inviwo/app" \
           -DIVW_EXTERNAL_MODULES="$1/inviwo/modules" \
           -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
           -DIVW_MODULE_FERMI=OFF \
           -DIVW_MODULE_GRAPH2D=ON \
           -DIVW_MODULE_PYTHON3=ON \
           -DIVW_MODULE_PYTHON3QT=ON \
           -DIVW_MODULE_QTWIDGETS=ON \
           -DIVW_MODULE_HDF5=ON

# Build the application.
make -j5

# Move the path import file to bin catalog.
cp "$1/scripts/ENVISIoNimport.py" ./bin

echo ""
echo ""
echo ""
echo "#####################################################################################"
echo "Inviwo has now been build with ENVISIoN."
echo "You can find and run the Inviwo and ENVISIoN application in bin directory:"
echo "$2/build/bin"
echo "######################################################################################"

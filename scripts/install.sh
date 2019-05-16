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

else
    echo "This installation script doesn't support your operating system"
    echo "Exiting..."
    exit 1
fi

# Get Inviwo repository and enter directory.
git clone https://github.com/inviwo/inviwo.git "$2"
cd "$2"

# Checkout correct version.
git checkout d20199dfd37c80559ce687243d296f6ce3e41c71

# Apply 2019 patch.
git apply < "$1/inviwo/patches/2019/envisionTransferFuncFix2019.patch"
git apply < "$1/inviwo/patches/2019/paneProperty2019.patch"
git apply < "$1/inviwo/patches/2019/tfRemoveFix2019.patch"

# Init and update submodules.
git submodule init

# Create and enter a build directory.
cd ..
mkdir build
cd build

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

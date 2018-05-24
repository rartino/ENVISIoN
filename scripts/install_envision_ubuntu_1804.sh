#!/usr/bin/env sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 envision_path inviwo_install_path"
    echo "Example: $0 /home/andkem/ENVISIoN /home/andkem/inviwo"
    exit 0
fi

grep 18.04 /etc/os-release 2>&1 > /dev/null
if [ $? -ne 0 ]; then
    echo "This installation script currently only supports Ubuntu 18.04."
    echo "Exiting!"
    exit 1
fi

sudo apt install git \
                 build-essential \
                 libpng-dev \
                 libhdf5-dev \
                 qtbase5-dev \
                 qttools5-dev \
                 gcc-6 \
                 g++-6 \
                 cmake \
                 python3-dev \
                 python3-numpy \
                 python3-h5py \
                 python3-regex \
                 libglu1-mesa-dev \
                 libxrandr-dev \
                 libxinerama-dev \
                 libxcursor-dev

git clone https://github.com/inviwo/inviwo.git "$2"

cd "$2"
mkdir build
cd build

export CC=gcc-6
export CXX=g++-6
cmake .. -D IVW_EXTERNAL_MODULES="$1/inviwo/modules" \
         -D IVW_MODULE_CRYSTALVISUALIZATIO=ON \
         -D IVW_MODULE_FERMI=OFF \
         -D IVW_MODULE_GRAPH2D=ON \
         -D IVW_MODULE_PYTHON3=ON \
         -D IVW_MODULE_PYTHON3QT=ON \
         -D IVW_MODULE_QTWIDGETS=ON \
         -D IVW_MODULE_HDF5=ON

echo "To build Inviwo with ENVISIoN:"
echo "Execute make in $2/build, i.e:"
echo ""
echo "cd \"$2/build\""
echo "make"
echo ""
echo "To speed up the build process, the argument -j <number of CPU
      cores + 1> can be given."
echo "Example: \"make -j5\" on a system with 4 cores."

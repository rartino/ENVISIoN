# TODO: 
#   *Remove inviwo source files.
#   *Remove unused build files.
#   *Probably a lot of non essensial packages.


FROM ubuntu:20.04
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get install -y \
        build-essential \
        curl \
        g++-8 \
        gcc-8 \
        git \
        libasound2 \
        libgtk-3-0 \
        libegl1-mesa \
        libfontconfig1 \
        libfreetype6 \
        libgdk-pixbuf2.0-0 \
        libgl1-mesa-glx \
        libglu1-mesa-dev \
        libhdf5-dev \
        libnss3-dev \
        libpng-dev \
        libtiff5-dev \
        libtirpc-dev \
        libxcomposite-dev \
        libxcomposite1 \
        libxcursor-dev \
        libxcursor1 \
        libxi-dev \
        libxi6 \
        libxinerama-dev \
        libxkbcommon-x11-0 \
        libxrandr-dev \
        libxrandr2 \
        libxss1 \
        libxtst6 \
        nodejs \
        npm \
        python3.7 \
        zlib1g-dev \
        python3 \
        python3-pip \
        python3-h5py

        # qtchooser

        # python3-regex \
RUN apt upgrade -y
RUN apt autoremove
        
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y qt5-default qtscript5-dev libssl-dev qttools5-dev qttools5-dev-tools qtmultimedia5-dev libqt5svg5-dev libqt5webkit5-dev libsdl2-dev libasound2 libxmu-dev libxi-dev freeglut3-dev libasound2-dev libjack-jackd2-dev libxrandr-dev libqt5xmlpatterns5-dev libqt5xmlpatterns5
        
# Clone repos
RUN git clone https://github.com/rartino/ENVISIoN
RUN git clone https://github.com/inviwo/inviwo
WORKDIR /inviwo
RUN git checkout v0.9.11
RUN git apply /ENVISIoN/inviwo/patches/2019/transferfunctionFix.patch
RUN git submodule update --init --recursive
RUN mkdir -p /inviwo-build
WORKDIR /inviwo-build



# # QT install
# WORKDIR /
# ARG QT_MAJOR=5.12
# ARG QT_MINOR=1
# ARG QT_VERSION=${QT_MAJOR}.${QT_MINOR}
# ADD qt-install-noninteractive.qs .
# RUN curl -LJO# "http://download.qt.io/official_releases/qt/${QT_MAJOR}/${QT_VERSION}/qt-opensource-linux-x64-${QT_VERSION}.run"
# RUN chmod +x qt-opensource-linux-x64-${QT_VERSION}.run
# RUN ./qt-opensource-linux-x64-${QT_VERSION}.run --script qt-install-noninteractive.qs --verbose --platform minimal
# RUN qtchooser -install opt-qt5.12.8 /usr/lib/qt5/bin/qmake


#RUN export CMAKE_PREFIX_PATH=/usr/lib/qt5/bin
# Python modules
RUN pip3 install --upgrade pip
RUN pip3 install \
         numpy \
         scipy \
         matplotlib \
         cmake \
         pytest

# Build inviwo
WORKDIR /inviwo-build
RUN cmake -G "Unix Makefiles" \
    -DCMAKE_C_COMPILER="gcc-8" \
    -DCMAKE_CXX_COMPILER="g++-8" \
    -DBUILD_SHARED_LIBS=ON \
    -DIVW_USE_EXTERNAL_IMG=ON \
    -DIVW_EXTERNAL_MODULES="/ENVISIoN/inviwo/modules" \
    -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
    -DIVW_MODULE_GRAPH2D=ON \
    -DIVW_MODULE_HDF5=ON \
    -DIVW_MODULE_PYTHON3=ON \
    -DIVW_MODULE_PYTHON3QT=ON \
    -DIVW_MODULE_QTWIDGETS=ON \
    ../inviwo
RUN make








# Install node packages
# WORKDIR /ENVISIoN
# RUN git checkout decoration_dev
# RUN pip3 uninstall -y h5py
# RUN pip3 install h5py
#RUN npm install





# Download inviwo
# Download envision

# Initialize inviwo
# Apply patches
# Cmake
# Build

# Node install




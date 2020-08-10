# When run will output a build to the /build_dir volume.
#
# Creates and image which can be used to build inviwo and envision.
# Will output packaged files to the /output volume.
#
# The /inviwo_src and /envision_src volumes are require to be provided 
# and not empty on image run. /build_dir and /output should be empty directories. 
#
# /build_dir volume is optional to provide but will make subsequent builds faster
# if provided as files then can be reused.
#
# example usage:
# ```
# docker build -t envision-builder -f packaging/docker/builder.Dockerfile .
# docker run envision-builder --rm -it \
#       -v /inviwo:/inviwo_src      # Path to inviwo source directory
#       -v /path/to/output:/output  # Path to desired package output
#       -v /path/to/build:/build_dir # Path to desired build directory


# Requires cloned and initialized inviwo and envision directories.
# Tested with inviwo version v0.9.11 other versions might require
# changes in configuration and dependencies.

FROM ubuntu:20.04
VOLUME ["/inviwo_src", "/build_dir", "/output"]

# Install dependencies
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
        build-essential gcc-8 g++-8 cmake git freeglut3-dev xorg-dev \
        openexr zlib1g zlib1g-dev \
        qt5-default qttools5-dev qttools5-dev-tools \
        python3 python3-pip \
        x11-utils \
        libjpeg-dev libtiff-dev libqt5svg5-dev libtirpc-dev libhdf5-dev \
        npm &&\
    apt upgrade -y && apt autoremove -y && apt clean -y

RUN pip3 install numpy h5py pybind11
COPY . /envision_src/

CMD cmake -G "Unix Makefiles" \
    -DCMAKE_C_COMPILER="gcc-8" \
    -DCMAKE_CXX_COMPILER="g++-8" \
    -DBUILD_SHARED_LIBS=ON \
    -DIVW_USE_EXTERNAL_IMG=ON \
    -DIVW_EXTERNAL_MODULES="/envision_src/inviwo/modules" \
    -DIVW_MODULE_CRYSTALVISUALIZATION=ON \
    -DIVW_MODULE_GRAPH2D=ON \
    -DIVW_MODULE_HDF5=ON \
    -DIVW_USE_EXTERNAL_HDF5=ON \
    -DIVW_MODULE_PYTHON3=ON \
    -DIVW_MODULE_PYTHON3QT=ON \
    -DIVW_MODULE_QTWIDGETS=ON \
    -DIVW_PACKAGE_PROJECT=ON \
    -DIVW_PACKAGE_INSTALLER=ON \
    -S /inviwo_src -B /build_dir && \
    cd /build_dir && \
    make -j2 && \
    make package && \
    echo "Build finished." && \
    echo "Installing envision..." && \
    cd /envision_src && \
    npm install && \
    cd /build_dir && \
    echo "Building .deb package" && \
    /envision_src/packaging/deb/repackage_deb.sh /envision_src && \
    echo "Building .tar package" && \
    /envision_src/packaging/tar/repackage_tar.sh /envision_src && \
    echo "Copying output files..." && \
    mv /build_dir/envision_2.1.0_amd64.tar.gz /output && \
    mv /build_dir/envision_2.1.0_amd64.deb /output && \
    echo "Done."
    
#/build_dir/envision_2.1.0_amd64.deb
#/build_dir/envision_2.1.0_amd64.tar.gz}
#           envision_2.1.0_amd64.tar.gz
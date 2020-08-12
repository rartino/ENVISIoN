# Dockerfile for building all of envision.
# Can be used either for generating linux packages 
# or the final docker image.

# Build and run final image:
# docker build -f packaging/docker/Dockerfile -t envision .
# docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro envision

# Generate packagees:
# docker build -f packaging/docker/Dockerfile --target envision_builder -t envision-builder .
# docker run -it --rm -v /path/to/output:/package_output envision-builder




# __Build stage to build inviwo__
FROM ubuntu:20.04 as inviwo_builder
ENV DEBIAN_FRONTEND=noninteractive
VOLUME ["/build_output"]
# Install dependencies
RUN apt update && \
    apt install -y \
        build-essential gcc-8 g++-8 cmake git freeglut3-dev xorg-dev \
        openexr zlib1g zlib1g-dev \
        qt5-default qttools5-dev qttools5-dev-tools \
        python3 python3-pip \
        x11-utils \
        libjpeg-dev libtiff-dev libqt5svg5-dev libtirpc-dev libhdf5-dev &&\
    apt upgrade -y && apt autoremove -y && apt clean -y
RUN apt install -y curl
RUN pip3 install numpy h5py pybind11

# Copy envision files required before inviwo build. 
# Do not copy all files to better utilize docker caching if other files change.
COPY /inviwo/patches /ENVISIoN/inviwo/patches
COPY /inviwo/modules /ENVISIoN/inviwo/modules

# Download and initialize inviwo
RUN git clone https://github.com/inviwo/inviwo --single-branch --branch v0.9.11 --recurse-submodules -j4 --depth 1
WORKDIR /inviwo
RUN git apply /ENVISIoN/inviwo/patches/deppack_fix.patch /ENVISIoN/inviwo/patches/filesystem_env.patch /ENVISIoN/inviwo/patches/ftl_fix.patch /ENVISIoN/inviwo/patches/transferfunction_extras.patch

# Configure and build inviwo.
RUN mkdir inviwo-build
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
    -DIVW_USE_EXTERNAL_HDF5=ON \
    -DIVW_MODULE_PYTHON3=ON \
    -DIVW_MODULE_PYTHON3QT=ON \
    -DIVW_MODULE_QTWIDGETS=ON \
    -DIVW_PACKAGE_PROJECT=ON \
    -DIVW_PACKAGE_INSTALLER=ON \
    -S /inviwo -B /inviwo-build
RUN make -j2 && make package

# If this stage is run copy build files to external volume
CMD cp -r /inviwo-build/* /build_output

# __Build stage to package envision__
FROM ubuntu:20.04 as envision_packager
ENV DEBIAN_FRONTEND=noninteractive
VOLUME ["/package_output"]
RUN apt update && apt install -y npm

# Copy build inviwo packages from previous stage
COPY --from=inviwo_builder /inviwo-build/Inviwo-v0.9.11.deb /
COPY --from=inviwo_builder /inviwo-build/Inviwo-v0.9.11.tar.gz /

# Install envision node modules
# Do not copy all files to better utilize docker caching if other files change.
COPY /package.json /package-lock.json /ENVISIoN/
WORKDIR /ENVISIoN
RUN npm install

# Copy rest of envision files
COPY . /ENVISIoN

# Build packages
WORKDIR /
RUN /ENVISIoN/packaging/deb/repackage_deb.sh /ENVISIoN
RUN /ENVISIoN/packaging/tar/repackage_tar.sh /ENVISIoN

# If this stage is run copy the packages to external volume.
CMD cp -t /package_output envision_2.1.0_amd64.deb envision_2.1.0_amd64.tar.gz

# __Build stage to install final envision application__
FROM ubuntu:20.04 as envision
ENV DEBIAN_FRONTEND=noninteractive
VOLUME ["/input_files"]
RUN apt update -y && apt upgrade -y && apt install -y python3-pip qt5-default qt5-doc python3 libhdf5-dev libtirpc3
RUN pip3 install --upgrade pip && pip3 install numpy scipy h5py regex

# Copy deb package from previous stage
COPY --from=envision_packager envision_2.1.0_amd64.deb /
RUN apt install -y ./envision_2.1.0_amd64.deb
RUN rm envision_2.1.0_amd64.deb

# Add installed pip modules to pythonpath. For some reason this
# is not done by default in docker python.
ENV PYTHONPATH=/usr/local/lib/python3.8/dist-packages

CMD envision

FROM ubuntu:20.04
# ENV TZ=Europe/Berlin
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV INVIWO_HOME="/inviwo-build/bin"
VOLUME ["/input", "/output"]

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
        build-essential gcc-8 g++-8 cmake git freeglut3-dev xorg-dev \
        qt5-default qttools5-dev qttools5-dev-tools \
        python3 python3-pip \
        x11-utils \
        libjpeg-dev libtiff-dev libqt5svg5-dev libtirpc-dev \
        npm &&\
    apt upgrade -y && apt autoremove -y && apt clean -y
        # qtchooser

        # python3-regex \

# RUN git clone https://github.com/rartino/ENVISIoN
RUN git clone https://github.com/inviwo/inviwo
WORKDIR /inviwo
RUN git checkout v0.9.11
RUN git submodule update --init --recursive

COPY / /ENVISIoN/
RUN git apply /ENVISIoN/inviwo/patches/2019/transferfunctionFix.patch

# Python modules
RUN pip3 install --upgrade pip && \ 
    pip3 install \
         numpy \
         scipy \
         matplotlib \ 
         h5py regex

#RUN export CMAKE_PREFIX_PATH=/usr/lib/qt5/bin
# Build inviwo
RUN mkdir -p /inviwo-build
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
RUN make -j3
# RUN rm -R /inviwo

# remove source files
# RUN rm -R /inviwo
# ENV LD_LIBRARY_PATH=/inviwo-build/lib
# ENV HDF5_DISABLE_VERSION_CHECK=1


WORKDIR /ENVISIoN
# RUN git checkout summer_2020
RUN npm install

# RUN rm -R /inviwo
# ENV INVIWO_HOME="/inviwo-build/bin"




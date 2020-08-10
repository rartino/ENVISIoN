# Creates an image with a runnable "envision" and "envision-inviwo" via X11.
# Before building image the .deb package must be built and 
# placed in the same folder as the build context.
# Example usage: 
#
# docker build -t envision -f /ENVISIoN/packaging/docker/envision.Dockerfile .
# xhost +local:docker
# docker run -it --rm \
#     --name envision \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
#     -v /path/to/vasp_files:/input_files
#     envision envision-inviwo
#
FROM ubuntu:20.04
RUN apt update -y && apt upgrade -y && apt install -y python3-pip
RUN pip3 install --upgrade pip && pip3 install  numpy scipy h5py regex
VOLUME ["/input_files"]
COPY envision_2.1.0_amd64.deb /
RUN DEBIAN_FRONTEND=noninteractive apt install -y ./envision_2.1.0_amd64.deb
RUN rm envision_2.1.0_amd64.deb
ENV PYTHONPATH=/usr/local/lib/python3.8/dist-packages
CMD envision

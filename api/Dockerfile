# Copyright (c) 2019-2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Default setting is building on nvidia/cuda:10.1-devel-ubuntu18.04
ARG BASE_IMAGE=nvidia/cuda:10.1-devel-ubuntu18.04

FROM ${BASE_IMAGE}
 
# Ensure apt-get won't prompt for selecting options
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            software-properties-common \
            autoconf \
            automake \
            build-essential \
            cmake \
            curl \
            git \
            wget \
            unzip \ 
            libopencv-dev \
            libopencv-core-dev \
            libssl-dev \
            libtool \
            pkg-config \
            python3 \
            python3-pip \
            python3-dev \
            python-flask \
	    nginx \
            rapidjson-dev \
            ffmpeg x264 libx264-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk2.0-dev pkg-config libavcodec-dev \
            libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev \
            libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
   
RUN pip3 install --upgrade wheel setuptools 
RUN pip3 install grpcio-tools

# Build expects "python" executable (not python3).
RUN rm -f /usr/bin/python && \
    ln -s /usr/bin/python3 /usr/bin/python

# Build the client library and examples
WORKDIR ./workspace
COPY tritton-client/VERSION .
COPY tritton-client/build build
COPY tritton-client/src/clients src/clients
COPY tritton-client/src/core src/core

RUN cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX:PATH=/workspace/install \
          -DTRTIS_ENABLE_GRPC_V2=ON && \
    make -j16 trtis-clients
RUN cd install && \
    export VERSION=`cat /workspace/VERSION` && \
    tar zcf /workspace/v$VERSION.clients.tar.gz *

RUN pip3 install --upgrade \
    install/python/tensorrtserver*.whl \
    install/python/triton*.whl

#compile opencv
RUN mkdir -p ~/opencv cd ~/opencv && \
    wget https://github.com/opencv/opencv/archive/4.2.0.zip && \
    unzip 4.2.0.zip && \
    rm 4.2.0.zip && \
    mv opencv-4.2.0 OpenCV && \
    cd OpenCV && \
    mkdir build && \ 
    cd build && \
    cmake .. && \
    make -j8 && \
    make install && \ 
    ldconfig    

ENV PATH //workspace/install/bin:${PATH}
ENV LD_LIBRARY_PATH /workspace/install/lib:${LD_LIBRARY_PATH}

ADD . ../api

WORKDIR ../api

RUN pip3 install -r requirements.txt

CMD ["uwsgi", "app.ini"]

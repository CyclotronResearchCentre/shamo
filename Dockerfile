FROM python:3.7 AS system-dependencies

RUN apt-get update && \
    apt-get install -y \
        libglu1-mesa \
        libxext-dev \
        libxrender-dev \
        libxtst-dev \
        libxcursor-dev \
        libxft2 \
        libxinerama1 \
        wget \
        openmpi-bin \
        libcgal-dev \
        libeigen3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O gmsh.tgz http://gmsh.info/bin/Linux/gmsh-git-Linux64-sdk.tgz && \
    tar -zxvf gmsh.tgz -C /opt && \
    rm gmsh* && \
    mv /opt/gmsh* /opt/gmsh

RUN wget -O getdp.tgz http://getdp.info/bin/Linux/getdp-3.2.0-Linux64c.tgz && \
    tar -zxvf getdp.tgz -C /opt && \
    rm getdp* && \
    mv /opt/getdp* /opt/getdp

ENV PATH=${PATH}:/opt/gmsh/bin/:/opt/getdp/bin/ \
    PYTHONPATH=${PYTHONPATH}:/opt/gmsh/lib/

RUN python -m pip install pygalmesh==0.4.0

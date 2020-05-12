ARG PY=3.7

# SYSTEM DEPENDENCIES ---------------------------------------------------------
# This stage installs all required system dependencies and makes sure to add
# them to the path.
FROM python:${PY}-buster AS sys-deps

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

# Install GetDP (http://getdp.info/)
RUN wget -O /tmp/getdp.tgz http://getdp.info/bin/Linux/getdp-3.2.0-Linux64c.tgz && \
    tar -zxvf /tmp/getdp.tgz -C /opt && \
    rm /tmp/getdp* && \
    mv /opt/getdp* /opt/getdp

# Add Gmsh and GetDP to the path
ENV PATH=${PATH}:/opt/gmsh/bin/:/opt/getdp/bin/ \
    PYTHONPATH=${PYTHONPATH}:/opt/gmsh/lib/

# PYTHON DEPENDENCIES ---------------------------------------------------------
# Pre install long term dependencies. Modifications made to 'requirements.txt'
# are installed at runtime.
FROM sys-deps AS py-deps

COPY requirements.txt /tmp/

RUN python -m pip install -r /tmp/requirements.txt

# TEST ------------------------------------------------------------------------
# Install dependencies for test stages and create a test user.
FROM py-deps AS test

RUN python -m pip install flake8 pytest tox

RUN useradd --create-home test
WORKDIR /home/test
USER test

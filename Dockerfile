ARG PY=3.7

# SYSTEM DEPENDENCIES ---------------------------------------------------------
# This stage installs all required system dependencies and makes sure to add
# them to the path.
FROM python:${PY}-buster AS sys-deps

MAINTAINER "Martin Grignard, mar.grignard@uliege.be"
LABEL maintainer="Martin Grignard, mar.grignard@uliege.be"
LABEL affiliation="GIGA CRC In vivo imaging, University of Liège, Liège, Belgium"
LABEL description="A tool for electromagnetic modelling of the head and sensitivity analysis."
LABEL link="https://github.com/CyclotronResearchCentre/shamo"

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
RUN wget -O /tmp/getdp.tgz http://getdp.info/bin/Linux/getdp-3.3.0-Linux64c.tgz && \
    tar -zxvf /tmp/getdp.tgz -C /opt && \
    rm /tmp/getdp* && \
    mv /opt/getdp* /opt/getdp

# Add Gmsh and GetDP to the path
ENV PATH=${PATH}:/opt/gmsh/bin/:/opt/getdp/bin/ \
    PYTHONPATH=${PYTHONPATH}:/opt/gmsh/lib/

# PYTHON DEPENDENCIES ---------------------------------------------------------
# Install python dependencies.
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

# DEPLOY ----------------------------------------------------------------------
# Create a usable docker with shamo installed.
FROM py-deps AS deploy

RUN useradd --create-home shamo
USER shamo

WORKDIR /tmp
COPY . /tmp/
RUN python setup.py install --user

WORKDIR /home/shamo


ENTRYPOINT ["python"]
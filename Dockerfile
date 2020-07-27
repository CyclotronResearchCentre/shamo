# BASE IMAGE --------------------------------------------------------------------------
FROM ubuntu:20.04 AS base

# Set timezone
RUN export TZ=Europe/Brussels && \
    ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
        libglu1-mesa \
        libxext-dev \
        libxrender-dev \
        libxtst-dev \
        libxcursor-dev \
        libxft2 \
        libxinerama1 \
        curl \
        libcgal-dev \
        libeigen3-dev \
        python3.8 \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*

# DOWNLOAD IMAGE ----------------------------------------------------------------------
FROM base as download

# Install GetDP
ENV APPS_PATH=/opt/apps \
    GETDP_VERSION=3.3.0 \
    GMSH_VERSION=4.6.0

RUN curl --progress-bar -o /tmp/getdp.tgz https://getdp.info/bin/Linux/getdp-${GETDP_VERSION}-Linux64c.tgz && \
    mkdir --parents ${APPS_PATH}/getdp && \
    tar -zxf /tmp/getdp.tgz -C ${APPS_PATH}/getdp && \
    rm /tmp/getdp* && \
    mv ${APPS_PATH}/getdp/getdp-${GETDP_VERSION}-Linux64 ${APPS_PATH}/getdp/${GETDP_VERSION} && \
    ln -s ${APPS_PATH}/getdp/${GETDP_VERSION} ${APPS_PATH}/getdp/getdp

RUN curl --progress-bar -o /tmp/gmsh.tgz https://gmsh.info/bin/Linux/gmsh-${GMSH_VERSION}-Linux64-sdk.tgz && \
    mkdir --parents ${APPS_PATH}/gmsh && \
    tar -zxf /tmp/gmsh.tgz -C ${APPS_PATH}/gmsh && \
    rm /tmp/gmsh* && \
    mv ${APPS_PATH}/gmsh/gmsh-${GMSH_VERSION}-Linux64-sdk ${APPS_PATH}/gmsh/${GMSH_VERSION} && \
    ln -s ${APPS_PATH}/gmsh/${GMSH_VERSION} ${APPS_PATH}/gmsh/gmsh

ENV PATH=${PATH}:${APPS_PATH}/getdp/${GETDP_VERSION}/bin

# PYTHON IMAGE ------------------------------------------------------------------------
FROM base AS python

COPY --from=download /opt /opt

ENV PATH=${PATH}:/opt/apps/getdp/getdp/bin:/opt/apps/gmsh/gmsh/bin \
    PYTHONPATH=${PYTHONPATH}:/opt/apps/gmsh/gmsh/lib \
    SHAMO_PATH=/opt/packages/shamo

RUN mkdir --parents ${SHAMO_PATH}

COPY . ${SHAMO_PATH}

RUN python3 -m pip install -r ${SHAMO_PATH}/requirements.txt && \
    python3 -m pip install -e ${SHAMO_PATH}


# SHAMO ONLY IMAGE --------------------------------------------------------------------
FROM python as shamo-only

# Create user
RUN useradd --create-home shamo
USER shamo
WORKDIR /home/shamo

ENTRYPOINT [ "python3" ]

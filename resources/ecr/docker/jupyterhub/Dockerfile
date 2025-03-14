# The build stage
# ---------------
# This stage is building Python wheels for use in later stages by using a base
# image that has more pre-requisites to do so, such as a C++ compiler.
#
# NOTE: If the image version is updated, also update it in ci/refreeze and
#       hub's Dockerfile!
#
FROM python:3.11-bullseye AS build-stage

# Setup SSH stuffs
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Build wheels
#
# We set pip's cache directory and expose it across build stages via an
# ephemeral docker cache (--mount=type=cache,target=${PIP_CACHE_DIR}). We use
# the same technique for the directory /tmp/wheels.
#
COPY requirements.txt requirements.txt
ARG PIP_CACHE_DIR=/tmp/pip-cache
RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    pip install build \
    && pip wheel \
    --wheel-dir=/tmp/wheels \
    -r requirements.txt

# The final stage
# ---------------
#
FROM python:3.11-slim-bullseye
ENV DEBIAN_FRONTEND=noninteractive

ENV FEAST_USAGE=False

ENV SHELL=/bin/bash

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    # basic utilities
    ca-certificates \
    wget \
    curl \
    gnupg \
    apt-transport-https \
    zip \
    unzip \
    htop \
    # network utilities
    dnsutils \
    iputils-ping \
    # process management
    tini \
    # version control
    git \
    openssh-client \
    # text editors
    vim \
    nano \
    # terminal multiplexer
    tmux \
    # build tools and compilers
    cmake \
    build-essential \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Conda
ENV CONDA_DIR=/opt/miniconda3
ENV CONDA_ENV_NAME=tqtensor
ENV PYTHON_VERSION=3.11
ENV NB_GID=100

RUN mkdir -p ${CONDA_DIR}
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ${CONDA_DIR}/miniconda.sh
RUN bash ${CONDA_DIR}/miniconda.sh -b -u -p ${CONDA_DIR}
RUN rm -rf ${CONDA_DIR}/miniconda.sh
RUN ${CONDA_DIR}/bin/conda init bash

# Create a Conda environment
RUN ${CONDA_DIR}/bin/conda create -y --name ${CONDA_ENV_NAME} python=${PYTHON_VERSION}

# Create a symbolic link to the Conda environment's Python
RUN rm -f /usr/local/bin/python && \
    ln -s ${CONDA_DIR}/envs/${CONDA_ENV_NAME}/bin/python /usr/local/bin/python

SHELL ["/opt/miniconda3/bin/conda", "run", "-n", "tqtensor", "/bin/bash", "-c"]
RUN conda install -y -c conda-forge nb_conda_kernels
RUN conda install -y -c conda-forge ipykernel

# Apply change permission script
COPY change_permissions.sh ${CONDA_DIR}/change_permissions.sh
RUN chmod +x ${CONDA_DIR}/change_permissions.sh
RUN ${CONDA_DIR}/change_permissions.sh ${CONDA_DIR}

# Init Conda with new terminal
RUN echo "source $HOME/.bashrc" >> ${HOME}/.bash_profile

# Install wheels built in the build-stage
COPY requirements.txt /tmp/requirements.txt
ARG PIP_CACHE_DIR=/tmp/pip-cache
RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    --mount=type=cache,from=build-stage,source=/tmp/wheels,target=/tmp/wheels \
    pip install \
    --find-links=/tmp/wheels/ \
    -r /tmp/requirements.txt

# The final stage
ENV NB_USER=tqtensor \
    NB_UID=1000 \
    HOME=/home/jupyterhub \
    NB_USER=tqtensor

RUN useradd \
    --no-log-init \
    -u ${NB_UID} \
    -g ${NB_GID} \
    --home-dir ${HOME} \
    ${NB_USER}

WORKDIR ${HOME}
USER ${NB_USER}

EXPOSE 8888
ENTRYPOINT ["tini", "--"]
CMD ["jupyter", "lab"]

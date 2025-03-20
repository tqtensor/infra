# The build stage
# ---------------
# This stage is building Python wheels for use in later stages by using a base
# image that has more pre-requisites to do so, such as a C++ compiler.
#
# NOTE: If the image version is updated, also update it in ci/refreeze and
#       hub's Dockerfile!
#
FROM python:3.11-bullseye AS build-stage

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
    -r requirements.txt \
    jupyterlab \
    jupyter_server

# The final stage
# ---------------
#
FROM python:3.11-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash
ENV NB_USER=jupyterhub \
    NB_UID=1000 \
    HOME=/home/jupyterhub

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

# Install wheels built in the build-stage
COPY requirements.txt /tmp/requirements.txt
ARG PIP_CACHE_DIR=/tmp/pip-cache
RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
    --mount=type=cache,from=build-stage,source=/tmp/wheels,target=/tmp/wheels \
    pip install \
    --find-links=/tmp/wheels/ \
    -r /tmp/requirements.txt \
    jupyterhub \
    jupyterlab

ENV NB_GID=100
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

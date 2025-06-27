# OBA Robot Development Container
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11-bullseye

# Container bilgileri
LABEL maintainer="OBA Robot Development Team"
LABEL description="Development environment for OBA Autonomous Garden Assistant Robot"

# Root olarak sistem paketlerini yükle
USER root

# APT paketlerini güncelle ve gerekli sistem paketlerini yükle
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Build tools
        build-essential \
        cmake \
        pkg-config \
        # Git and development tools
        git \
        curl \
        wget \
        nano \
        vim \
        tree \
        htop \
        # Hardware simulation dependencies
        xvfb \
        x11-utils \
        # OpenCV dependencies
        libopencv-dev \
        python3-opencv \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libgtk2.0-dev \
        libatlas-base-dev \
        gfortran \
        # GPIO simulation tools
        i2c-tools \
        # Network tools
        net-tools \
        iputils-ping \
        # Audio support (opsiyonel robot ses feedback için)
        alsa-utils \
        pulseaudio \
        # Graphics support (simulation için)
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        # Cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies için pip upgrade
RUN python3 -m pip install --upgrade pip setuptools wheel

# GPIO Mock kütüphanelerini yükle (Raspberry Pi simülasyonu için)
RUN pip3 install \
    fake-rpi \
    gpiozero \
    pigpio \
    fake-rpi-gpio

# Simulation dependencies
RUN pip3 install \
    pygame \
    pymunk \
    matplotlib \
    plotly \
    jupyter \
    notebook \
    ipywidgets

# Development tools
RUN pip3 install \
    black \
    pylint \
    flake8 \
    pytest \
    pytest-cov \
    mypy \
    isort \
    bandit \
    safety

# Web development tools
RUN pip3 install \
    flask-cors \
    flask-restful \
    gunicorn \
    redis

# Computer Vision tools
RUN pip3 install \
    imutils \
    scikit-image \
    dlib

# Workspace setup directory oluştur
RUN mkdir -p /workspace-setup

# User'a geri dön
USER vscode

# Virtual display setup (GUI simülasyon için)
ENV DISPLAY=:99

# Python path
ENV PYTHONPATH=/workspace

# Workspace directory
WORKDIR /workspace

# Default command
CMD ["bash"]

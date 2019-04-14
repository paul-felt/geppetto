FROM ubuntu:18.04
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

# openai gym/baselines prereqs
RUN apt-get update && \
        apt-get -y install \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-opengl \
        libjpeg-dev \
        libboost-all-dev \
        libsdl2-dev \
        libosmesa6-dev \
        patchelf \
        ffmpeg \
        xvfb \
        wget \
        cmake \
        unzip \
        git 

    # upgrade pipe
RUN pip3 install --upgrade pip

# install pip requirements 
COPY ./requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt

# baselines (pip install doesn't work--tries to install mujoco)
RUN git clone https://github.com/openai/baselines.git && \
    pip3 install -e baselines

# create a non-root user for jupyter
RUN useradd -ms /bin/bash jupyter
USER jupyter

# get run script in place
COPY ./openai-jupyter-start.sh /
COPY ./jupyter_notebook_config.json /home/jupyter/.jupyter/jupyter_notebook_config.json

# CMD defaults to firing up jupyter

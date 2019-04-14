#FROM tensorflow/tensorflow:latest-gpu-py3
FROM tensorflow/tensorflow:1.12.0-rc0-py3
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

# openai gym/baselines prereqs
RUN apt-get update && apt-get -y install \
    python3-dev \
    python-opengl \
    ffmpeg \
    xvfb \
    cmake \
    libopenmpi-dev \
    zlib1g-dev \
    libxrender1 \
    git

# pip 
RUN pip3 install --upgrade pip
COPY ./requirements.txt /
COPY ./openai-jupyter-start.sh /
RUN pip3 install -r /requirements.txt

# baselines (pip install doesn't work--tries to install mujoco)
RUN git clone https://github.com/openai/baselines.git && \
    pip install -e baselines

# CMD defaults to firing up jupyter

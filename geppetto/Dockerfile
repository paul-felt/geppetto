FROM ubuntu
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

# package in the current code base
ADD . /code
ADD ./data /data
WORKDIR /code

# python deps
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-pip libpython-dev
RUN pip install -r requirements.txt

# geppetto
CMD [ "python", "server.py" ]

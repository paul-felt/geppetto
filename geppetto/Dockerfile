FROM ubuntu
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

# python deps
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  libpython3-dev \
  vim \
  telnet \
  curl 
# do this up front so they get cached (good for development iteration)
RUN pip3 install Flask==1.0.2 \
  crossbar==18.9.2 \
  redis==2.10.3 \
  gevent==1.1.0 \
  flask-restplus==0.11.0

# package in the current code base
ADD . /code
WORKDIR /code

# this is the definitive list of reqs. Respect them
RUN pip3 install -r requirements.txt

# geppetto
#CMD [ "python", "server.py" ]
CMD [ "crossbar", "start" ]

FROM crossbario/autobahn-python-armhf
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

COPY ./requirements.txt /

# packages
RUN apk add alpine-sdk && apk add python3-dev

# pip 
RUN pip3 install -r /requirements.txt

ADD . /code
WORKDIR /code

# TODO: discover the geppetto server
CMD python3 client.py --host plfelt-mbp.local --web-port=80 --wamp-port=5555

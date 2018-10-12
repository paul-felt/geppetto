FROM crossbario/autobahn-python
#FROM crossbario/autobahn-python-armhf
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

COPY ./requirements.txt /

# pip 
RUN pip3 install -r /requirements.txt

ADD . /code
WORKDIR /code
COPY ./geppetto_client.py /code/

# TODO: discover the geppetto server
CMD python3 client.py --host plfelt-mbp.local --web-port=8080 --wamp-port=5555

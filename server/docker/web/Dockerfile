#FROM tiangolo/uwsgi-nginx-flask:python3.7-alpine3.7
FROM tiangolo/uwsgi-nginx-flask:python3.7
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

COPY ./requirements.txt /

# pip 
RUN pip3 install -r /requirements.txt


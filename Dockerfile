FROM kennethreitz/pipenv:latest

LABEL Name=buzzbird Version=0.0.1

RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/logs/django
WORKDIR /usr/src/app

ADD . /usr/src/app

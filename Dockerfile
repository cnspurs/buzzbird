FROM kennethreitz/pipenv:latest

LABEL Name=buzzbird Version=0.0.1

RUN groupadd -r www -g 1000 && useradd -u 1000 -r -g www -s /sbin/nologin www
RUN mkdir /usr/src/app
RUN chown www:www -R /usr/src/app
USER www
RUN mkdir -p /usr/src/app/logs/django
RUN mkdir -p /usr/src/app/static/media
RUN mkdir -p /usr/src/app/sessions
RUN chown www:www /usr/src/app/sessions

WORKDIR /usr/src/app

ADD . /usr/src/app

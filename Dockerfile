FROM kennethreitz/pipenv:latest

LABEL Name=buzzbird Version=0.0.1

RUN groupadd -r www -g 1000 && useradd -u 1000 -r -g www -s /sbin/nologin www
RUN mkdir -p /usr/src/app/logs/django
RUN mkdir -p /usr/src/app/static/media
RUN mkdir -p /usr/src/app/sessions
RUN chown -R 1000:1000 /usr/src/app/
USER 1000:1000
WORKDIR /usr/src/app
ADD --chown=1000:1000 . /usr/src/app
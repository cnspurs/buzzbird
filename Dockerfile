FROM python:3.8.13-slim-bullseye

LABEL Name=buzzbird Version=0.2.0

RUN pip install poetry==1.1.12
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
WORKDIR /app
RUN poetry install -n

RUN apt-get update
RUN apt-get install -y netcat

RUN groupadd -r www -g 1000 && useradd -u 1000 -r -g www -s /sbin/nologin www
RUN mkdir -p /usr/src/app/logs/django
RUN mkdir -p /usr/src/app/static/media
RUN mkdir -p /usr/src/app/sessions
RUN mkdir -p /home/www && chown -R 1000:1000 /home/www
RUN chown -R 1000:1000 /usr/src/app/
USER 1000:1000
WORKDIR /usr/src/app
ADD --chown=1000:1000 . /usr/src/app

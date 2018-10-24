#!/bin/bash

python3 manage.py migrate --noinput
python3 manage.py init_admin
python3 manage.py init_twittermember
python3 manage.py collectstatic --noinput
gunicorn -b 0.0.0.0:3000 buzzbird.wsgi
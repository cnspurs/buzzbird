#!/bin/bash
python3 manage.py migrate --noinput
python3 manage.py init_admin
python3 manage.py runserver 0.0.0.0:3000

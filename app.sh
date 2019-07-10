#!/bin/bash

echo "Waiting for postgres..."

while ! nc -z app 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py migrate --noinput
python3 manage.py init_admin
python3 manage.py collectstatic --noinput
gunicorn -b 0.0.0.0:3000 buzzbird.wsgi
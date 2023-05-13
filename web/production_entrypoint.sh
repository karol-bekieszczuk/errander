#!/bin/sh
/opt/venv/bin/python3 manage.py makemigrations
until /opt/venv/bin/python3 manage.py migrate --no-input
do
  echo 'migration failed, retrying'
  sleep 1
done
/opt/venv/bin/python3 manage.py loaddata accounts/accounts.json
/opt/venv/bin/python3 manage.py collectstatic --no-input
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm errander.wsgi:application --bind "0.0.0.0:${APP_PORT:-8000}"
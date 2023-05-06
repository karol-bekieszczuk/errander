#!/bin/sh
cd web
until /opt/venv/bin/python3 manage.py migrate
do
  echo 'migration failed, retrying'
  sleep 1
done
APP_PORT=${PORT:-8000}
/opt/venv/bin/python3 manage.py loaddata accounts/accounts.json
/opt/venv/bin/python3 manage.py collectstatic --no-input
#/opt/venv/bin/gunicorn --bind 0.0.0.0:8000 errander.wsgi
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm errander.wsgi:application --bind "0.0.0.0:${APP_PORT}"
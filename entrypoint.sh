#!/bin/sh
cd app
until python manage.py migrate
do
  echo 'migration failed, retrying'
  sleep 1
done
python manage.py loaddata accounts/accounts.json
python manage.py collectstatic --no-input
gunicorn --bind 0.0.0.0:8000 errander.wsgi
#!/bin/sh
/opt/venv/bin/python3 manage.py makemigrations
until /opt/venv/bin/python3 manage.py migrate --no-input
do
  echo 'migration failed, retrying'
  sleep 1
done
/opt/venv/bin/python3 manage.py loaddata accounts/accounts.json
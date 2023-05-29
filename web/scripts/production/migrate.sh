#!/bin/sh
/opt/venv/bin/python3 manage.py makemigrations
/opt/venv/bin/python3 manage.py migrate --no-input
/opt/venv/bin/python3 manage.py loaddata accounts/accounts.json
#!/bin/sh
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm errander.wsgi:application --bind "0.0.0.0:${APP_PORT:-8000}"
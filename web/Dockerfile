FROM python:3.8-alpine

WORKDIR /web

RUN apk update && \
 apk add --no-cache python3-dev libc-dev libffi-dev postgresql-libs && \
 apk add --no-cache bash

COPY requirements.txt .

RUN \
 python3 -m venv /opt/venv && \
 pip install --upgrade pip && \
 apk add --no-cache --virtual .build-deps g++ gcc musl-dev postgresql-dev && \
 /opt/venv/bin/pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . /web

EXPOSE 8000
FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt .

RUN \
 apk update && \
 pip install --upgrade pip && \
 apk add --no-cache python3-dev libc-dev libffi-dev && \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps g++ gcc musl-dev postgresql-dev && \
 pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps && \
 apk add --no-cache bash

COPY . .

EXPOSE 8000
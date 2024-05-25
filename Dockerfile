FROM python:3.12-slim-bullseye
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD requirements.txt /app/

RUN python3 -m pip install -r requirements.txt --no-cache-dir

ADD ./ /app/
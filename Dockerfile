FROM python:3.9.6-alpine

WORKDIR src/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#RUN apk add build-base postgresql-dev libpq --no-cache --virtual .build-dep

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
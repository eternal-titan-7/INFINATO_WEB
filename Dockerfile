FROM debian:latest

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential curl wget

FROM python:3.9.9-slim-buster

RUN python -m venv env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN pip install -U pip
RUN mkdir /INFINATO/
WORKDIR /INFINATO/
COPY . /INFINATO/
RUN pip install -U -r requirements.txt
CMD gunicorn --threads 1000 -w 1 app:app
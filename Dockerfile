FROM ubuntu:latest

FROM python:3.10-slim-buster

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential curl wget

RUN python -m venv env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN pip install -U pip
RUN mkdir /INFINATO/
WORKDIR /INFINATO/
COPY . /INFINATO/
RUN pip install -U -r requirements.txt
CMD gunicorn --threads 1000 -w 1 app:app
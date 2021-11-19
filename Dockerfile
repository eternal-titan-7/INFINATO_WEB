FROM ubuntu:latest

RUN apt update && apt upgrade -y

FROM python:3.9.9-slim-buster

RUN python -m venv env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN pip install -U pip
RUN mkdir /INFINATO/
WORKDIR /INFINATO/
COPY . /INFINATO/
RUN pip install -U -r requirements.txt
CMD gunicorn -k eventlet -w 1 main:app
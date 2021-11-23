FROM ubuntu:latest

RUN apt update && apt upgrade -y

FROM gcc:latest

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
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
RUN curl http://archive.ubuntu.com/ubuntu/pool/main/g/gcc-defaults/gcc_9.3.0-1ubuntu2_amd64.deb -o gcc.deb
RUN apt install ./gcc.deb
RUN rm ./gcc.deb
CMD gunicorn --threads 1000 -w 1 app:app
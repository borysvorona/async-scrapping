FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD . /code

RUN apt update --fix-missing && pip install --no-cache-dir --requirement requirements.txt

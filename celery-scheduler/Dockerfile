FROM python:3.6-alpine

WORKDIR /home/docker/celery
COPY /celery-scheduler /home/docker/celery
COPY .env /home/docker/celery

RUN pip install -r requirements.txt

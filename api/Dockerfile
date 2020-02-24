FROM python:3.6-alpine

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

WORKDIR /home/docker/api
COPY /api /home/docker/api
COPY .env /home/docker/api

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5001

RUN pip install gunicorn

# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "app:app"]
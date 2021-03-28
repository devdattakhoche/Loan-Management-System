FROM ubuntu:16.04

MAINTAINER <<Devdatta Khoche>>
RUN apt-get update -y && \
   apt-get install -y python-pip python-dev
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "docker-script.sh" ]
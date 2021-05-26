FROM ubuntu:20.04


RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR ./app

RUN apt -qq update

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata
RUN pip install ffmpeg-python
RUN apt -qq install -y git python3-pip
RUN add-apt-repository ppa:jon-severinsson/ffmpeg
RUN apt-get update
RUN apt-get install ffmpeg

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

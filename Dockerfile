FROM ubuntu:20.04

sudo add-apt-repository ppa:jon-severinsson/ffmpeg
sudo apt-get update
sudo apt-get install ffmpeg

RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR ./app

RUN apt -qq update

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata
RUN pip install ffmpeg-python
RUN apt -qq install -y git python3-pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

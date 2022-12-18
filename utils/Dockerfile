FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3

COPY . /opt/utils

RUN pip3 install -r /opt/utils/python/requirements.txt
FROM ghcr.io/maxotta/kiv-ds-docker:latest

RUN yum -q -y install python3

COPY . /opt/node

RUN pip3 install -r /opt/node/python/requirements.txt

CMD /usr/bin/python3 /opt/node/python/main.py
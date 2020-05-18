FROM nodered/node-red-docker
MAINTAINER <psykobug@github>

# for permissions
USER root

RUN \
# upgrade programs
  apt-get -y update \
  && apt-get -y upgrade \
# install zip
  && apt-get install zip \
# install tree
  && apt-get install tree \
# install python3.7, migth be unnecessary for later nodered/node-red-docker images
  && cd /usr/src \
  && wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz \
  && tar xzf Python-3.7.2.tgz \
  && cd Python-3.7.2 \
  && ./configure --enable-optimizations \
  && make altinstall \
# install astropy
  && pip3.7 install astropy



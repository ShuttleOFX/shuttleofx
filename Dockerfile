# Set the base image to Ubuntu
FROM tuttleofx/tuttleofx:latest

# File Author / Maintainer
MAINTAINER ShuttleOFX <shuttleofx-dev@googlegroups.com>

# Update repository, Download and Install
RUN apt-get update && apt-get install -y vim wget python-setuptools python-pip nodejs-legacy npm xdg-utils libpython2.7 python-flask docker.io timelimit ruby-full
RUN pip install pymongo python-oauth2 flask-oauthlib && gem install travis -v 1.8.2 --no-rdoc --no-ri

#Install last mongodb version to have text search feature
RUN cd /opt/ && \
    wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-3.0.6.tgz && \
    tar -zxvf mongodb-linux-x86_64-3.0.6.tgz && \
    mv mongodb-linux-x86_64-3.0.6 mongodb && \
    mkdir /opt/mongo-data

# Expose ports
EXPOSE 5000
EXPOSE 5004
EXPOSE 5002
EXPOSE 5005
EXPOSE 27017

ENV SHUTTLEOFX_DEV=/opt/shuttleofx_git
ENV PATH=${PATH}:/opt/mongodb/bin

COPY . ${SHUTTLEOFX_DEV}
RUN cd ${SHUTTLEOFX_DEV}/shuttleofx_client/ && npm install && npm install -g grunt-cli && grunt build

RUN git config --global user.email shuttleofx@googlegroups.com && git config --global user.name "ShuttleOFX" 

# Hack for genarts plugins
RUN mkdir -p /usr/genarts/SapphireOFX && cp ${SHUTTLEOFX_DEV}/etc/usr-genarts-SapphireOFX-s_config.text /usr/genarts/SapphireOFX/s_config.text

RUN chmod 777 ${SHUTTLEOFX_DEV}/start.sh

CMD ["/opt/shuttleofx_git/start.sh"]


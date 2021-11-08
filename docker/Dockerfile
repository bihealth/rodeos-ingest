FROM python:3.8-buster

MAINTAINER Clemens Messerschmidt <messersc@bih-charite.de>
LABEL org.opencontainers.image.source https://github.com/bihealth/rodeos-ingest

ARG app_git_url=https://github.com/bihealth/rodeos-ingest.git
ARG app_git_tag=master
ARG app_git_depth=1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static
# As long as we serve from internal cubi-gitlab via SSH
ENV GIT_SSH_COMMAND "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Copy source code into Docker image
RUN mkdir -p /usr/src/app
RUN git clone --depth $app_git_depth --branch $app_git_tag $app_git_url /usr/src/app

# Install system dependencies
#RUN apt-get update && \
#    apt-get install -y \
#        apt-utils \
#        gcc \
#        ldap-utils \
#        libldap2-dev \
#        libsasl2-dev \
#        make \
#        postgresql-client \
#        wget

RUN cd /usr/src/app && \
    pip install --no-cache-dir -r requirements/base.txt

# Define the entry point
COPY docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]
#ENTRYPOINT ["python -V"]

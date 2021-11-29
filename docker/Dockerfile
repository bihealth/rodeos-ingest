FROM python:3.8-buster

LABEL org.opencontainers.image.source https://github.com/bihealth/rodeos-ingest

ARG app_git_url=https://github.com/messersc/rodeos-ingest.git
ARG app_git_tag=feature/docker
ARG app_git_depth=1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static
# As long as we serve from internal cubi-gitlab via SSH
ENV GIT_SSH_COMMAND "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

# Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Copy source code into Docker image
WORKDIR /usr/src/app
RUN git clone --depth "$app_git_depth" --branch feature/docker https://github.com/messersc/rodeos-ingest.git

COPY . /usr/src/app/rodeos-ingest
#COPY .github/workflows/ci/irods_environment-rods.json /root/.irods/irods_environment.json

RUN apt-get update && \
    apt-get install -y \
        wget \
        hashdeep \
        multiarch-support \
        vim tree less htop
        #lsb-release \

RUN wget -qO - https://packages.irods.org/irods-signing-key.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.irods.org/apt/ xenial main" \
    | tee /etc/apt/sources.list.d/renci-irods.list

RUN wget security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb && dpkg -i libssl1.0.0_1.0.1t-1+deb8u12_amd64.deb

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        irods-icommands 

WORKDIR /usr/src/app/rodeos-ingest
RUN pip install -e .
#RUN pip install --no-cache-dir -r requirements/base.txt
RUN pip install --no-cache-dir -r requirements/test.txt # TODO remove
#RUN pip freeze

# Define the entry point
COPY docker/docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]

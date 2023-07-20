# Copyright (c) 2016-present Mattermost, Inc. All Rights Reserved.
# See License.txt for license information.
ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE}

RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*;

ENV MYSQL_ROOT_PASSWORD=mostest
ENV MYSQL_USER=mmuser
ENV MYSQL_PASSWORD=mostest
ENV MYSQL_DATABASE=mattermost_test

#
# Configure Mattermost
#
WORKDIR /mm

# Copy over files
ADD https://releases.mattermost.com/7.10.2/mattermost-team-7.10.2-linux-amd64.tar.gz .
RUN tar -zxvf mattermost-team-*-linux-amd64.tar.gz && rm mattermost-team-*-linux-amd64.tar.gz
COPY config_docker.json ./mattermost/config/config_docker.json
COPY docker-entry.sh .


RUN chmod +x ./docker-entry.sh
ENTRYPOINT ./docker-entry.sh

# Mattermost environment variables
ENV PATH="/mm/mattermost/bin:${PATH}"

# Create default storage directory
RUN mkdir ./mattermost-data
# VOLUME /mm/mattermost-data


# Ports
EXPOSE 8065

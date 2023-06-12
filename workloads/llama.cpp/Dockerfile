#ARG BASE=ubuntu
#ARG VERSION=latest
#
#FROM ${BASE}:${VERSION} as build

ARG BASE=ubuntu:latest

FROM ${BASE} as build

RUN apt-get update && \
    apt-get install -y build-essential

COPY . .

RUN make

ENTRYPOINT [ "/main" ]

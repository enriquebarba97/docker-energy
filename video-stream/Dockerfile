ARG BASE=ubuntu
ARG VERSION=latest

FROM ${BASE}:${VERSION} as build

RUN apt-get update && \
    apt-get install -y vlc

RUN useradd -m vlcuser

COPY fragment.mp4 .

CMD su vlcuser -c "cvlc -vvv "fragment.mp4" --play-and-exit --sout '#standard{access=http,mux=ts,dst=0.0.0.0:8080}'"
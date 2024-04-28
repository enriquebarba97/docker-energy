ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE} as build

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

COPY server.c server.c

RUN gcc -o server server.c

ENTRYPOINT ["./server"]
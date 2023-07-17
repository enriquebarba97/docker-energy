ARG BASE=ubuntu:latest

FROM ${BASE} as build

RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg && rm -rf /var/lib/apt/lists/*;

ENTRYPOINT ["ffmpeg"]
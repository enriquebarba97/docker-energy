ARG BASE=ubuntu:latest

FROM ${BASE} as build

RUN apt-get update && apt-get install --no-install-recommends -y redis-server && rm -rf /var/lib/apt/lists/*;

EXPOSE 6379

CMD ["redis-server", "--protected-mode no"]
ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE} as build

RUN apt-get update && apt-get install -y wget make build-essential ltrace \
    && wget https://download.redis.io/redis-stable.tar.gz \
    && tar -xvzf redis-stable.tar.gz \
    && cd redis-stable \
    && make \
    && make install

EXPOSE 6379

COPY entrypoint.sh /entrypoint.sh

CMD ["entrypoint.sh"]
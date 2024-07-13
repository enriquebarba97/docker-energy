ARG BASE=ubuntu@sha256:565d62d2283a7cc4b3d759d9a97a5bfcebeb341166f9076a4df504f8f106cd54

FROM ${BASE} as build

ENV REDIS_VERSION 7.2.4
ENV MALLOC=libc

RUN apt-get update && apt-get install -y wget make build-essential \
    && wget "https://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz" \
    && tar -xvzf "redis-$REDIS_VERSION.tar.gz" \
    && cd "redis-$REDIS_VERSION" \
    && make "MALLOC=$MALLOC"\
    && make install

EXPOSE 6379

WORKDIR /logs

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
ARG BASE=ubuntu@sha256:565d62d2283a7cc4b3d759d9a97a5bfcebeb341166f9076a4df504f8f106cd54

FROM ${BASE} as build

RUN apt-get update \
    && apt-get install -y build-essential libelf-dev libdw-dev libunwind-dev git \
    && git clone https://github.com/namhyung/uftrace.git \
    && cd uftrace \
    && misc/install-deps.sh \
    && ./configure \
    && make \
    && make install \
    && cd ..

WORKDIR /app

COPY server.c server.c

RUN gcc -pg -o server server.c

WORKDIR /logs

ENTRYPOINT ["uftrace", "record", "/app/server"]
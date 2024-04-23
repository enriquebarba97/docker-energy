ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE} as build

RUN apt-get update && apt-get install -y wget make build-essential cmake git \
    && git clone https://github.com/enriquebarba97/memcpy-benchmark.git \
    && cd memcpy-benchmark/ \
    && cmake . && make


FROM ${BASE}

COPY  --from=build /memcpy-benchmark/test_memcpy /test_memcpy

ENTRYPOINT ["/test_memcpy"]
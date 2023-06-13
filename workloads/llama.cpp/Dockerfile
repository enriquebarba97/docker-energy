ARG BASE=ubuntu:latest

FROM ${BASE} as build

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential && rm -rf /var/lib/apt/lists/*;

COPY . .

RUN make

ENTRYPOINT [ "/main" ]

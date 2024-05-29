ARG BASE=ubuntu@sha256:565d62d2283a7cc4b3d759d9a97a5bfcebeb341166f9076a4df504f8f106cd54

FROM ${BASE} as build

RUN apt-get update \
    && apt-get install -y build-essential

WORKDIR /app

COPY server.c server.c

RUN gcc -o server server.c

ENTRYPOINT ["./server"]
# ENTRYPOINT ["uftrace","record","-P",".","./server"]
# ENTRYPOINT ["uftrace","record","./server"]
# ENTRYPOINT ["perf","record","./server"]
# ENTRYPOINT ["strace", "-o", "trace.log", "-C", "-T", "./server"]
ARG BASE=ubuntu@sha256:565d62d2283a7cc4b3d759d9a97a5bfcebeb341166f9076a4df504f8f106cd54

FROM ${BASE} as build

RUN apt-get update && apt-get install -y build-essential

# RUN apt-get update \
#     && apt-get install -y linux-tools-common linux-tools-generic linux-tools-`uname -r` \
#     && apt-get install -y build-essential libelf-dev libdw-dev libunwind-dev git \
#     && git clone https://github.com/namhyung/uftrace.git \
#     && cd uftrace \
#     && misc/install-deps.sh -y \
#     && ./configure \
#     && make \
#     && make install

WORKDIR /app

COPY test_memcpy.c test_memcpy.c

RUN gcc -o test_memcpy test_memcpy.c

ENTRYPOINT ["./test_memcpy"]
# ENTRYPOINT ["uftrace","record","-P",".","./test_memcpy"]
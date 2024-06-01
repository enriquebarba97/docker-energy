ARG BASE=ubuntu@sha256:565d62d2283a7cc4b3d759d9a97a5bfcebeb341166f9076a4df504f8f106cd54

FROM ${BASE} as build

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

COPY memcpy_12.c memcpy_12.c

RUN gcc -o test_memcpy memcpy_12.c

FROM ${BASE}

WORKDIR /app

COPY --from=build /app/test_memcpy .

ENTRYPOINT ["./test_memcpy"]

ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE} as build

COPY --from=binary . .

COPY --from=model /7B/ggml-model-q4_0.bin ./models/7B/ggml-model-q4_0.bin

ENTRYPOINT [ "/main" ]

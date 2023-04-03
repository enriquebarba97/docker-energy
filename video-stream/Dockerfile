ARG VERSION=latest

FROM ubuntu:${VERSION} as build

RUN apt-get update && \
    apt-get install -y vlc

RUN useradd -m vlcuser

# WORKDIR /stream

COPY fragment.mp4 .

FROM ubuntu:${VERSION} as runtime

COPY --from=build . .

# ENTRYPOINT /stream
CMD su vlcuser -c "cvlc -vvv "fragment.mp4" --play-and-exit --sout '#standard{access=http,mux=ts,dst=localhost:8080}'"
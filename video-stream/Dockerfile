ARG VERSION=latest

FROM debian:${VERSION} as build

RUN apt-get update && \
    apt-get install -y vlc

RUN useradd -m vlcuser

# WORKDIR /stream

COPY fragment.mp4 .

FROM debian:${VERSION} as runtime

COPY --from=build . .

# ENTRYPOINT /stream
CMD su vlcuser -c "cvlc -vvv "fragment.mp4" --play-and-exit --sout '#standard{access=http,mux=ts,dst=0.0.0.0:8080}'"
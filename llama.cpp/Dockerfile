ARG UBUNTU_VERSION=11.6

FROM debian:$UBUNTU_VERSION as build

RUN apt-get update && \
    apt-get install -y build-essential

WORKDIR /app

COPY . .

RUN make

FROM debian:$UBUNTU_VERSION as runtime

COPY --from=build /app/main /main

ENTRYPOINT [ "/main" ]
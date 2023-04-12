ARG BASE=ubuntu
ARG VERSION=latest

FROM ${BASE}:${VERSION} as build

RUN apt-get update && \
    apt-get install -y build-essential

# WORKDIR /app

COPY . .

RUN make


# FROM ${BASE}:${VERSION} as runtime

# # COPY --from=build /app/main /main
# COPY --from=build . .

ENTRYPOINT [ "/main" ]

ARG BASE=ubuntu:latest

FROM ${BASE} as build

ENV TZ=Europe/Amsterdam
ENV DIST=debian
ENV VERSION=15
ENV PATH="${PATH}:/usr/lib/postgresql/${VERSION}/bin"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y wget gnupg lsb-release \
    && echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update && apt-get install --no-install-recommends -y postgresql-${VERSION} postgresql-contrib-${VERSION} && rm -rf /var/lib/apt/lists/*;

EXPOSE 5432

COPY docker-entry.sh .

COPY pg_hba.conf /etc/postgresql/${VERSION}/main/pg_hba.conf

RUN chmod +x ./docker-entry.sh \
    && echo "listen_addresses='*'" >> /etc/postgresql/${VERSION}/main/postgresql.conf \
    && rm -rf /var/lib/postgresql/${VERSION}/main \
    && mkdir -p /var/lib/postgresql/${VERSION}/main \
    && chown -R postgres:postgres /var/lib/postgresql/${VERSION}/main

USER postgres

ENTRYPOINT ./docker-entry.sh && tail -f /dev/null

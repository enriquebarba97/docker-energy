ARG BASE=ubuntu:latest

FROM ${BASE} as build

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=Europe/Amsterdam

RUN apt-get update && apt-get install -y postgresql postgresql-contrib


EXPOSE 5432

COPY docker-entry.sh .

RUN chmod +x ./docker-entry.sh

USER postgres
# ENV PGUSER postgres
# ENV PGPASSWORD postgres
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

ENTRYPOINT ./docker-entry.sh
# ENTRYPOINT ./docker-entry.sh && tail -f /dev/null
# CMD postgres

ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE}

ENV NODE_VERSION 16.20.0

RUN apt-get update && apt-get install -y curl xz-utils \
    && ARCH= && dpkgArch="$(dpkg --print-architecture)" \
    && case "${dpkgArch##*-}" in \
      amd64) ARCH='x64';; \
      ppc64el) ARCH='ppc64le';; \
      s390x) ARCH='s390x';; \
      arm64) ARCH='arm64';; \
      armhf) ARCH='armv7l';; \
      i386) ARCH='x86';; \
      *) echo "unsupported architecture"; exit 1 ;; \
    esac \
    && set -ex \
    && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$ARCH.tar.xz" \
    && tar -xJf "node-v$NODE_VERSION-linux-$ARCH.tar.xz" -C /usr/local --strip-components=1 --no-same-owner \
    && ln -s /usr/local/bin/node /usr/local/bin/nodejs \
    && npm install -g yarn && rm -rf /var/lib/apt/lists/*; npm cache clean --force; rm "node-v$NODE_VERSION-linux-$ARCH.tar.xz"

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install && yarn cache clean;

COPY . .

ENV NODE_ENV=development

RUN yarn db:seed:dev && \
    yarn predev:cognito:ci

EXPOSE 3001

CMD [ "yarn", "start:api:watch" ]
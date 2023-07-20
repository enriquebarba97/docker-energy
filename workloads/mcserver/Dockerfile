ARG BASE=ubuntu@sha256:b060fffe8e1561c9c3e6dea6db487b900100fc26830b9ea2ec966c151ab4c020

FROM ${BASE}

RUN apt-get update && apt-get install --no-install-recommends -y openjdk-17-jdk openjdk-17-jre && rm -rf /var/lib/apt/lists/*;

WORKDIR /app

COPY . /app

EXPOSE 25565:25565

CMD java -Xmx1024M -Xms1024M -jar server-1.19.1.jar nogui
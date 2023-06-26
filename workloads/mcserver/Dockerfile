ARG BASE=ubuntu:latest

FROM ${BASE}

RUN apt-get update && apt-get install -y openjdk-17-jdk openjdk-17-jre

WORKDIR /app/

ADD . /app/

EXPOSE 25565:25565

CMD java -Xmx1024M -Xms1024M -jar server-1.19.1.jar nogui
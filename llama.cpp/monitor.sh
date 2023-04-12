#!/bin/bash

# Get the arguments
while getopts "b:n:i:t:" arg; do
  case $arg in
    b) BASE=$OPTARG;;
    n) NUMBER=$OPTARG;;
    i) INFERENCE=$OPTARG;;
    t) TOKENS=$OPTARG;;
  esac
done

# Default values
BASE=${BASE:-ubuntu}
NUMBER=${NUMBER:-1}
INFERENCE=${INFERENCE:-"Building a website can be done in 10 simple steps:"}
TOKENS=${TOKENS:-512}

# If alpine is selected, use the alpine Dockerfile;
if [[ "$BASE" == "alpine" ]]; then 
  DOCKERFILE=DockerfileAlpine; 
# If centos is selected, use the centos Dockerfile
elif [[ "$BASE" == "centos" ]]; then
  DOCKERFILE=DockerfileCentos;
else 
  DOCKERFILE=Dockerfile; 
fi

# Build the Docker image
docker build -t llama.cpp -f $DOCKERFILE --build-arg BASE=$BASE .

# Warm up workload (prime number test)
sysbench cpu --cpu-max-prime=100000 --threads=2 run

# Run and monitor the workload for the specified number of times
for ((i=1; i<=$NUMBER; i++))
do
  sleep 10
  perf stat -o result.txt --append -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ sleep 180 &\
  docker run --rm -v $PWD/models:/models llama.cpp -m /models/7B/ggml-model-q4_0.bin -p "$INFERENCE" -n $TOKENS --seed 12345678
done

docker rmi llama.cpp
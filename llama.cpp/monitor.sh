#!/bin/bash

# Get the arguments
while getopts "b:n:" arg; do
  case $arg in
    b) BASE=$OPTARG;;
    n) NUMBER=$OPTARG;;
  esac
done

# Default values
BASE=${BASE:-ubuntu}
NUMBER=${NUMBER:-1}

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

# Run and monitor the workload for the specified number of times
for ((i=1; i<=$NUMBER; i++))
do
  perf stat -o result.txt --append -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ docker run --rm -v $PWD/models:/models llama.cpp -m /models/7B/ggml-model-q4_0.bin -p "The capital of The Netherlands:" -n 20
done

docker rmi llama.cpp
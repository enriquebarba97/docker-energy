#!/bin/bash
perf stat -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ docker run -v /home/bailey/Documents/llama/models:/models llama.cpp -m /models/7B/ggml-model-q4_0.bin -p "The capital of The Netherlands:" -n 20

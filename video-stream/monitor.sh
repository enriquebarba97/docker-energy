#!/bin/bash
perf stat -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ docker run -p 8080:8080 --add-host=host.docker.internal:host-gateway video-stream
#!/bin/bash

# Set timestamp to variable in unix format
TIMESTAMP=$(date +%s)

# Run ls and print result to log timestamp file
ltrace -f -o /logs/ltrace-$TIMESTAMP.log redis-server --protected-mode no
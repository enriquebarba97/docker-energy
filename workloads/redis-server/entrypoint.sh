#!/bin/bash

# Set timestamp to variable in unix format
TIMESTAMP=$(date +%s)

# Run with ltrace if the environment variable is set
# Else, run without ltrace
if [ "$LTRACE" = true ]; then
  exec uftrace record -P . redis-server --protected-mode no
else
  exec redis-server --protected-mode no
fi
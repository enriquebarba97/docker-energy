#!/bin/bash

# init array of pids

# run processes and store pids in array
for i in `seq 0 1`
do
    echo "Running client $i"
    ./client $i &
done

wait

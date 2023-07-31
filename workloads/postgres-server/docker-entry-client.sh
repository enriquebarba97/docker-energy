#!/bin/bash
set -e

pgbench -i -s 50 testdb

pgbench -c 10 -t 500000 testdb
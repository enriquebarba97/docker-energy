#!/bin/bash
set -e

pgbench -i -s 50 testdb

pgbench -c 10 -T 500 testdb
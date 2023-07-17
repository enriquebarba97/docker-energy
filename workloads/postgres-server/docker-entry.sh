#!/bin/bash
set -e

# PGPASSWORD=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PASSWORD_USER=postgres

service postgresql start
# initdb -D /var/lib/postgresql/data
# postgres -D /var/lib/postgresql/data

createdb testdb

pgbench -i -s 50 testdb

pgbench -c 1 -j 2 -T 10 testdb
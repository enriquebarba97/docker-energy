#!/bin/bash
set -e

if [[ "$DIST" == "centos" ]]; then
  initdb -D /var/lib/pgsql/14/data
  pg_ctl -D /var/lib/pgsql/14/data start &
else
  initdb -D /var/lib/postgresql/14/main
  postgres -D /var/lib/postgresql/14/main -c config_file=/etc/postgresql/14/main/postgresql.conf &
fi

sleep 5
createdb -U postgres testdb

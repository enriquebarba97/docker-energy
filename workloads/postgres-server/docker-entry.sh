#!/bin/bash
set -e

if [[ "$DIST" == "centos" ]]; then
  initdb -D /var/lib/pgsql/${VERSION}/data
  pg_ctl -D /var/lib/pgsql/${VERSION}/data start &
else
  initdb -D /var/lib/postgresql/${VERSION}/main
  postgres -D /var/lib/postgresql/${VERSION}/main -c config_file=/etc/postgresql/${VERSION}/main/postgresql.conf &
fi

sleep 5
createdb -U postgres testdb

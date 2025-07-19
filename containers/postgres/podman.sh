#!/usr/bin/env sh

podman build -t hawat-pg . ;

podman run \
    --name hawat-db \
    -v ~/.pgdata/hawat:/var/lib/postgresql/data \
    -v ~/.secrets:/etc/secrets \
    -e POSTGRES_PASSWORD_FILE=/etc/secrets/pgpwf \
    -e POSTGRES_USER=hawat \
    -p 5431:5432 \
    -d hawat-pg

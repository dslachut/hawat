#!/usr/bin/env sh

podman build -t hawat-pg . ;

podman run \
    --name hawat-db \
    -e POSTGRES_PASSWORD_FILE=/etc/secrets \
    -v /custom/mount:/var/lib/postgresql/data
    -d hawat-pg

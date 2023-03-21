#!/bin/sh

echo "boot start"

args="--salt=$SALT"

[ -n "$TLS" ] && args="$args --tls=$TLS"

[ -n "$PORT" ] && args="$args --port=$PORT"

[ -n "$ISOLATE" ] && args="$args --isolate-rooms"

[ -n "$PASSWORD" ] && args="$args --password=$PASSWORD"

if [ -n "$MOTD" ]; then
  echo "$MOTD" >> /app/syncplay/motd
  args="$args --motd-file=/app/syncplay/motd"
fi

PYTHONUNBUFFERED=1 exec syncplay-server $args $@

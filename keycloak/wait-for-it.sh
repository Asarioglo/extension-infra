#!/bin/bash
# wait-for-it.sh: wait until a host and port are available

host="$1"
shift
port="$1"
shift

while ! nc -z $host $port; do
  echo "Waiting for $host:$port..."
  sleep 1
done

echo "$host:$port is available"
exec "$@"
#!/usr/bin/env sh

# setting envirnment variables
#export $(egrep -v '^#' .env | xargs)
set -e

# loop checking if PostgreSQL server is ready yet
until PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -q -c '\q'; do
  >&2 echo "Postgres is unavailable -- sleeping..."
  sleep 1
done

# server ready
>&2 echo "Postgres is up!"

# running commands
exec "$@"
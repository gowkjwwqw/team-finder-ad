#!/bin/sh
set -e

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "PostgreSQL launched"

python manage.py migrate
python manage.py runserver 0.0.0.0:8000

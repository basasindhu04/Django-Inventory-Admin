#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py makemigrations inventory
python manage.py migrate

# Seed data if it does not exist
python manage.py seed_data

exec "$@"

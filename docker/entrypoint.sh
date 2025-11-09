#!/bin/sh
set -e

export PYTHONPATH=/app

echo "Running database setup..."
python app/scripts/setup_db.py

echo "Seeding test users..."
python app/scripts/test_seed_users.py

echo "Running application tests..."
python -m app.tests.test_cards_routes


echo "Starting application..."
exec "$@"

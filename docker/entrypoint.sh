#!/bin/sh
set -e

export PYTHONPATH=/app

echo "Running database setup..."
python app/scripts/setup_db.py

echo "Starting application..."
exec "$@"

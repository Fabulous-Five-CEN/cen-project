#!/bin/sh
set -e

export PYTHONPATH=/app
APP_ENV=${APP_ENV:-development}

echo "Running database setup..."
python app/scripts/setup_db.py

if [ "$APP_ENV" = "production" ]; then
  echo "Production environment detected; running seeders..."
  python -m unittest app.scripts.test_seed_users
  python -m unittest app.scripts.seed_essential_vocab
fi


if [ "$APP_ENV" = "demo" ]; then
  echo "Demo environment detected; running seeders w/ demo..."
  python -m unittest app.scripts.demo_seed_users
  python -m unittest app.scripts.seed_essential_vocab
fi


echo "Starting application..."
exec "$@"

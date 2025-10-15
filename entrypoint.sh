#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput

# Optionally create a superuser on first run if env vars provided
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
fi

# Start server
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}

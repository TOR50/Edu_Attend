#!/usr/bin/env bash
set -euo pipefail

/opt/conda/bin/python manage.py migrate --noinput
/opt/conda/bin/python manage.py collectstatic --noinput

# Optionally create a superuser on first run if env vars provided
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  /opt/conda/bin/python manage.py createsuperuser --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
fi

# Start server
exec /opt/conda/bin/gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}

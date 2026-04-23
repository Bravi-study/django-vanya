#!/bin/sh
set -e

/app/.venv/bin/python manage.py migrate --noinput
/app/.venv/bin/python manage.py collectstatic --noinput

exec "$@"

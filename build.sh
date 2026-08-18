#!/usr/bin/env bash
set -o errexit

python manage.py migrate --no-input
python manage.py import_campers
python manage.py create_accounts

exec gunicorn conectados.wsgi:application

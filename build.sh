#!/usr/bin/env bash
set -o errexit

python manage.py migrate --no-input
python manage.py import_campers
python manage.py create_accounts
python manage.py create_superusers
python manage.py export_users

exec gunicorn conectados.wsgi:application

#!/bin/sh

python3 manage.py collectstatic --no-input

service cron start

python3 manage.py prune_files

exec "$@"
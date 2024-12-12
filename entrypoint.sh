#!/bin/sh

service cron start

python3 manage.py prune_files

exec "$@"


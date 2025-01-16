#!/usr/bin/env bash

# перенос переменных окружения контейнера в cron
# https://habr.com/ru/companies/redmadrobot/articles/305364/
set -e

# переносим значения переменных из текущего окружения
env | while read -r LINE; do  # читаем результат команды 'env' построчно
    # делим строку на две части, используя в качестве разделителя "=" (см. IFS)
    IFS="=" read VAR VAL <<< ${LINE}
    # удаляем все предыдущие упоминания о переменной, игнорируя код возврата
    sed --in-place "/^${VAR}/d" /etc/security/pam_env.conf || true
    # добавляем определение новой переменной в конец файла
    echo "${VAR} DEFAULT=\"${VAL}\"" >> /etc/security/pam_env.conf
done

python3 manage.py collectstatic --no-input
python3 manage.py migrate

service cron start

python3 manage.py prune_files

exec "$@"
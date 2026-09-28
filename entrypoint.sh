#!/bin/sh
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Применяем миграции..."
    python manage.py migrate --noinput

    echo "Собираем статику..."
    python manage.py collectstatic --noinput
else
    echo "Пропускаем миграции (RUN_MIGRATIONS=false) — этим занимается сервис web."
fi

exec "$@"
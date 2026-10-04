# DEPLOYMENT

Деплой проекта palliativ: Django (gunicorn) + Huey + PostgreSQL + Redis за Nginx, всё в Docker Compose. Автоматизация через GitHub Actions (`.github/workflows/deploy.yml`).

## 1. Архитектура на сервере

Проект лежит на сервере в `~/site` (пользователь `deploy`). Запущено 5 контейнеров:

| Сервис | Контейнер | Образ | Назначение |
|--------|-----------|-------|------------|
| `web` | `palliativ_web` | `ghcr.io/ramazantoichuev/palliativ:latest` | Django + gunicorn (`config.wsgi`, 3 воркера, порт 8000 внутри сети) |
| `huey` | `palliativ_huey` | тот же образ | Фоновые задачи (`python manage.py run_huey`) |
| `nginx` | `palliativ_nginx` | `nginx:alpine` | Единственный открытый порт: 80. Раздаёт `/static/`, `/media/`, проксирует остальное в `web:8000` |
| `db` | `palliativ_db` | `postgres:18.4-alpine` | База данных, volume `postgres_data`, порт наружу не публикуется |
| `redis` | `palliativ_redis` | `redis:8.10-alpine` | Кеш/очередь, порт наружу не публикуется |

Особенности:

- `web` и `huey` используют готовый образ из ghcr.io, на сервере образ не собирается (`image:` вместо `build:`).
- `web` и `huey` монтируют `.:/app`: код, который реально выполняется на сервере, берётся из каталога `~/site` (поэтому пайплайн делает `git pull`), а образ даёт окружение и зависимости.
- Контейнер `web` запускается с `RUN_MIGRATIONS=true`, `huey` с `RUN_MIGRATIONS=false` (управляется в `entrypoint.sh`).
- `web` и `huey` стартуют только после того, как `db` и `redis` стали healthy.
- Настройки приложения лежат в `.env` на сервере (в репозитории его нет): `DB_NAME`, `DB_USER`, `DB_PASSWORD` и др.

### Nginx и Gunicorn

Запросы идут по цепочке: браузер → Nginx (порт 80) → Gunicorn (`web:8000`, 3 воркера) → Django. Приложение напрямую наружу не опубликовано, снаружи доступен только Nginx. Конфиг лежит в `nginx.conf` и монтируется в контейнер как `/etc/nginx/conf.d/default.conf`:

- `/static/` отдаётся Nginx из `/app/staticfiles/`, `/media/` из `/app/media/`;
- всё остальное проксируется в `web:8000` с заголовками `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.

Проверка: открыть `http://<IP сервера>/` в браузере, страница должна отдаваться через Nginx.

### Лимит размера загружаемых файлов

Размер файла ограничивается на двух уровнях, и значения должны быть согласованы:

| Уровень | Параметр | Значение |
|---------|----------|----------|
| Django | `MAX_RESOURCE_FILE_SIZE_MB` | 40 МБ (файлы ресурсов, точная проверка размера) |
| Django | `MAX_IMAGE_SIZE_MB` | 25 МБ (изображения, меньше лимита ресурсов, отдельная настройка Nginx не нужна) |
| Nginx | `client_max_body_size` в `nginx.conf` | 100m |

Почему так: если лимит Nginx меньше, чем у Django, файл 20–40 МБ получит ошибку 413 от Nginx и до Django не дойдёт (при значении 20m так и было). Лимит Nginx (100 МБ) намеренно выше лимита Django (40 МБ): в теле запроса помимо файла есть служебные данные multipart-формы, а запас позволяет не трогать Nginx при небольших изменениях лимитов приложения. Точный отказ по размеру выдаёт Django со своим понятным сообщением. Главное правило: `client_max_body_size` не должен быть меньше наибольшего лимита Django. Если `MAX_RESOURCE_FILE_SIZE_MB` вырастет выше 100, нужно поднять и `client_max_body_size`. После правки `nginx.conf` выполнить `docker compose restart nginx`.

### ALLOWED_HOSTS и CSRF_TRUSTED_ORIGINS

Django отвечает `400 Bad Request` на запросы, у которых заголовок `Host` не входит в `ALLOWED_HOSTS`. Nginx передаёт тот `Host`, по которому пришёл запрос (IP сервера или домен), поэтому этот адрес должен быть в списке.

Значения заданы списками прямо в `config/settings.py`, а не через `.env`. Сейчас в `ALLOWED_HOSTS` входят:

- `localhost` и `127.0.0.1` (нужны для health-check в `DEPLOY`, который ходит на `http://localhost/`);
- `37.139.26.171` (IP сервера);
- два dev-адреса ngrok.

`CSRF_TRUSTED_ORIGINS` содержит только `https://`-адреса ngrok. Для работы по HTTP на IP сервера он не нужен: запросы с того же адреса Django считает однородными.

Проверка, что хост пропускается (на сервере):

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: 37.139.26.171" http://localhost/   # ожидается 200
```

Как изменить список:

1. Отредактировать `ALLOWED_HOSTS` (и `CSRF_TRUSTED_ORIGINS`) в `config/settings.py`, закоммитить и смержить в `main`. Пайплайн развернёт новую версию.
2. При смене IP заменить значение в списке. После появления домена добавить домен в `ALLOWED_HOSTS`, а в `CSRF_TRUSTED_ORIGINS` добавить `https://<домен>`.
3. `localhost` и `127.0.0.1` из списка не убирать, иначе health-check получит 400.

Возможное улучшение: читать эти списки из `.env` через `env.list(...)`, чтобы менять хосты без коммита.

## 2. CI/CD пайплайн

Файл: `.github/workflows/deploy.yml`, workflow `Deploy`.

Workflow срабатывает на `push` и на `pull_request` в `main`, но по-разному:

- **PR в `main`:** выполняется только `TEST`. Сборка, миграции и деплой пропускаются (у `BUILD&PUSH` стоит `if: github.event_name == 'push'`, остальные зависят от него через `needs`).
- **Пуш или мерж в `main`:** выполняются все четыре job'а.

Четыре job'а выполняются строго последовательно (`needs`): если любой падает, следующие не запускаются.

| # | Job | Что делает |
|---|-----|------------|
| 1 | `TEST` | Поднимает postgres 18.4 и redis 8.10 как service-контейнеры, ставит зависимости на Python 3.13, запускает `ruff check . --exit-zero` и `python manage.py test` |
| 2 | `BUILD&PUSH` | Собирает образ и публикует в `ghcr.io/ramazantoichuev/palliativ` с тегами `latest` и `<commit sha>` |
| 3 | `MIGRATE` | По SSH на сервере: `git pull origin main`, логин в ghcr.io, `docker compose pull web`, `docker compose run --rm web python manage.py migrate --noinput` |
| 4 | `DEPLOY` | По SSH: логин в ghcr.io, `docker compose pull`, `docker compose up -d`, `docker compose restart nginx` (Nginx заново находит пересозданный `web`) и health-check `curl` на `http://localhost/` с повторами до минуты. Скрипт останавливается на первой ошибке (`script_stop: true`), при неудачной проверке в лог выводятся `docker compose ps` и логи `web`/`nginx`, job падает |

Права workflow: `contents: read`, `packages: write` (нужны для публикации образа в ghcr.io через `GITHUB_TOKEN`).

### Секреты (GitHub → Settings → Secrets and variables → Actions)

| Секрет | Назначение |
|--------|------------|
| `SSH_PRIVATE_KEY` | Приватный ключ, созданный отдельно для CI (без пароля) |
| `SERVER_HOST` | Адрес сервера |
| `SERVER_USER` | Пользователь на сервере (`deploy`) |
| `DB_URL` | Строка подключения к БД для миграций |

В репозитории секретов нет. `GITHUB_TOKEN` выдаётся GitHub автоматически.

### Ротация ключа CI

1. `ssh-keygen -t ed25519 -N "" -C "github-actions-deploy" -f ./gha_deploy`
2. Добавить `gha_deploy.pub` в `~/.ssh/authorized_keys` пользователя `deploy`.
3. Заменить секрет `SSH_PRIVATE_KEY` содержимым файла `gha_deploy`.
4. Убедиться, что пайплайн проходит, затем удалить старый ключ с сервера и локальные файлы.

## 3. Доступ к серверу

- Пользователь `deploy` с `sudo` и доступом к Docker.
- Вход только по SSH-ключу, вход под root заблокирован, firewall включён (открыт порт 80 и SSH).
- Ключи людей и ключ CI хранятся в `~/.ssh/authorized_keys` пользователя `deploy`. Сами публичные ключи в репозитории не публикуем, здесь только реестр с отпечатками.

### Реестр ключей

| # | Владелец | Тип | Отпечаток (SHA256) |
|---|----------|-----|--------------------|
| 1–3 | (заполнить: владельцы уже добавленных ключей) | | |
| 4 | a.nuria.m02@gmail.com | ssh-rsa (4096) | `9KvureK8AEjnPIp88XOZsWUcrHOUE6VKy/29aEzByAc` |
| 5–6 | (ожидают добавления) | | |

Ключ CI в реестре отмечается отдельной строкой (`github-actions-deploy`).

### Добавление нового ключа

На сервере под пользователем `deploy`:

```bash
echo '<публичный ключ целиком>' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Проверка с компьютера нового пользователя: `ssh deploy@<IP>`. После этого добавить строку в реестр выше.
Отпечаток ключа считается командой `ssh-keygen -lf <файл.pub>`.

### Удаление ключа

Удалить строку с нужным ключом из `~/.ssh/authorized_keys` и убрать запись из реестра.

## 4. Postgres и Redis

- Postgres 18.4 и Redis 8.10 запущены в Docker Compose, оба с healthcheck'ами; порты на хост не публикуются.
- Данные Postgres лежат в volume `postgres_data` и переживают перезапуск контейнера.
- Приложение подключается под ролью `django_app` без прав суперпользователя; строка подключения передаётся через `DB_URL`.
- Бэкап Postgres настроен через cron и проверен. (Заполнить: расписание, куда пишутся копии, срок хранения, команда восстановления.)

## 5. Ручной деплой (если GitHub Actions недоступен)

На сервере:

```bash
cd ~/site
git pull origin main
docker compose pull
docker compose run --rm web python manage.py migrate --noinput
docker compose up -d
curl -f http://localhost/
```

## 6. Откат

Автоматического отката нет. Образы с тегом `<commit sha>` сохраняются в ghcr.io, поэтому для отката нужно:

1. Переключить `~/site` на нужный коммит (`git checkout <sha>`).
2. Указать в `docker-compose.yml` образ с тегом этого коммита вместо `latest` и выполнить `docker compose up -d`.
3. При необходимости откатить миграции вручную: `docker compose run --rm web python manage.py migrate <app> <номер>` (если они обратимы).

## 7. Диагностика

- Статус и логи запусков: вкладка **Actions** в репозитории.
- Логи приложения: `docker compose logs --tail 100 web` (и `nginx`, `huey`, `db`) на сервере.
- Упал `TEST`: исправить код или тесты, образ не собирается, деплоя нет.
- Упал `MIGRATE`: на сервере остаётся прежняя версия контейнеров, деплой не выполняется.
- Упал `DEPLOY`: смотреть `docker compose ps` и логи `web`/`nginx`, health-check ждёт ответ 200 на `http://localhost/`.

## 8. Известные ограничения

- Nginx разрешает имя `web` в IP при старте, а `web` пересоздаётся при каждом деплое, поэтому после обновления `web` выполняется `docker compose restart nginx`. Без этого nginx мог бы продолжать отдавать 502 на старый адрес.
- Логин в ghcr.io делается токеном `GITHUB_TOKEN`, который действует только до конца job'а, поэтому логин нужен в каждом job'е, который делает `docker compose pull` (`MIGRATE` и `DEPLOY`). Альтернатива: один раз войти на сервере токеном `read:packages`.
- `ruff` запускается с `--exit-zero`, то есть замечания по стилю не останавливают пайплайн.
- Домен и HTTPS пока не настроены: сайт работает по HTTP на 80 порту (Let's Encrypt будет добавлен после появления домена).
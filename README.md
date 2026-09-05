Palliativ
Веб-приложение для системы паллиативной помощи, разработанное на Django.

Стек технологий
Python 3.12
Django 6.1
PostgreSQL
django-bootstrap5
django-modeltranslation
Pillow
psycopg 3
python-dotenv
Структура проекта
palliativ/
├── accounts/          # приложение пользователей
├── config/            # настройки проекта
├── locale/            # файлы локализации
├── main/              # основное приложение
├── media/             # загружаемые файлы
├── news/              # новости
├── templates/         # HTML-шаблоны
├── .env.example
├── manage.py
└── requirements.txt
Требования
Перед запуском необходимо установить:

Python 3.11+
PostgreSQL
pip
virtualenv (или venv)
GNU gettext — нужен только для работы с переводами (makemessages / compilemessages)
Для Ubuntu/Debian:

sudo apt update
sudo apt install -y python3-venv libpq-dev postgresql postgresql-contrib gettext
Для Windows:

winget install --id mlocati.GettextIconv
После установки перезапустите терминал, чтобы msgfmt и xgettext появились в PATH.
Клонирование проекта
git clone https://github.com/ramazantoichuev/palliativ.git
cd palliativ
git checkout dev
Создание виртуального окружения
Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate
Windows:

python -m venv .venv
.venv\Scripts\activate
Установка зависимостей
pip install -r requirements.txt
Настройка переменных окружения
Скопируйте пример конфигурации:

cp .env.example .env
Заполните необходимые значения в файле .env:

DB_NAME=palliativ
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-secret-key
DEBUG=True
Настройка базы данных
Создайте пользователя и базу данных PostgreSQL:

CREATE USER palliativ WITH PASSWORD 'password';
ALTER USER palliativ CREATEDB;
CREATE DATABASE palliativ OWNER palliativ;
Применение миграций
python manage.py migrate
Создание суперпользователя
python manage.py createsuperuser
Запуск проекта
python manage.py runserver
После запуска приложение будет доступно по адресу:

http://127.0.0.1:8000/
Административная панель:

http://127.0.0.1:8000/admin/
Полезные команды
Создать миграции:

python manage.py makemigrations
Применить миграции:

python manage.py migrate
Собрать статические файлы:

python manage.py collectstatic
Запустить Django shell:

python manage.py shell
Локализация (RU / KY / EN)
В проекте две независимые системы перевода.

Инициализация групп и прав пользователей:
python manage.py setup_moderator_group
python manage.py setup_manager_group

1) Интерфейс — gettext. Строки в коде и шаблонах оборачиваются в gettext_lazy()
и {% translate %}. Переводы лежат в locale/<язык>/LC_MESSAGES/django.po,
а Django читает скомпилированный django.mo рядом с ним.
Основной язык — русский: исходные строки русские, поэтому при отсутствии
перевода показывается русский текст.

2) Контент — django-modeltranslation. Для полей, перечисленных в news/translation.py
и events/translation.py, в таблицах созданы колонки title_ru / title_ky / title_en и т.п.
Заполняются вручную в админке (вкладки по языкам). Обязателен только русский,
при пустом значении остальные языки подхватывают fallback на ru.

Переключатель RU / KY / EN находится в общей навигации (templates/base.html)
и отправляет POST на /i18n/setlang/. Выбор сохраняется в cookie,
URL разделов при этом не меняются.

Пересборка переводов интерфейса
Требуется установленный GNU gettext (см. раздел Требования).

Шаг 1. Собрать новые строки из кода и шаблонов в .po:

python manage.py makemessages -l ky -l en --ignore=.venv
Шаг 2. Открыть locale/ky/LC_MESSAGES/django.po и locale/en/LC_MESSAGES/django.po
и заполнить msgstr у новых записей. Каталога locale/ru нет и не нужно —
русский берётся из самих msgid.

Записи с пометкой "#, fuzzy" — черновой перевод, подставленный автоматически.
В django.mo они НЕ попадают. Проверьте перевод и удалите строку "#, fuzzy",
иначе строка останется непереведённой.

Шаг 3. Скомпилировать .mo:

python manage.py compilemessages --ignore=.venv
Шаг 4. Перезапустить сервер — каталог переводов кешируется в памяти процесса.

Важно: django.po и django.mo коммитятся в репозиторий парой.
Если изменить .po и не пересобрать .mo, на сайте перевод не появится.

Добавление нового языка
Добавьте код языка в LANGUAGES в config/settings.py, затем:

python manage.py makemessages -l <код>
python manage.py makemigrations
python manage.py migrate
Миграции нужны, чтобы modeltranslation создал колонки нового языка
для переводимых полей моделей.

Разработка
Основная ветка разработки:

dev
Перед началом работы рекомендуется:

git checkout dev
git pull origin dev
Для новых задач создавайте отдельные feature-ветки:

git checkout -b feature/task-name








Линтер (ruff)
В проекте используется ruff (https://docs.astral.sh/ruff/) — пока только
проверка кода (ruff check); автоформатирование (ruff format) сознательно
не применяется, чтобы не создавать конфликтов открытым веткам.

Конфигурация лежит в pyproject.toml: базовые правила (E4/E7/E9/F),
сортировка импортов (I) и Django-проверки (DJ); каталоги migrations/ и
locale/ исключены. Ruff ставится вместе с остальными зависимостями:
pip install -r requirements.txt.

Проверить код перед коммитом:

ruff check .

Автоматически исправить то, что чинится без участия человека
(сортировка импортов, неиспользуемые импорты):

ruff check . --fix

Точечно подавить правило можно комментарием "# noqa: <код правила>",
но по умолчанию лучше исправлять код. Новые правила добавляем в
pyproject.toml только по договорённости в команде.

Запуск проекта через ngrok

Для локальной разработки с внешним доступом (вебхуки, тестирование на других устройствах) используется статический домен ngrok.

Установка ngrok

Windows:
winget install ngrok -s msstore

macOS:
brew install ngrok

Либо скачать напрямую с ngrok.com/download — подходит для обеих ОС.

Авторизация

Получи свой authtoken на dashboard.ngrok.com/get-started/your-authtoken и выполни (одинаково для Windows и macOS):

ngrok config add-authtoken твой_authtoken

Запусти Django-сервер

Убедись, что сервер слушает порт 8000 (или другой — но тогда поменяй порт в команде ngrok ниже):

python manage.py runserver 8000

Запусти ngrok с привязкой к статическому домену

В отдельном терминале (Django-сервер должен продолжать работать в первом):

ngrok http 8000 --url https://hatchling-causal-doornail.ngrok-free.dev

Важно: порт после ngrok http должен совпадать с портом, на котором реально запущен Django (8000 в примере выше, а не 80).

После запуска сайт будет доступен по адресу:
https://hatchling-causal-doornail.ngrok-free.dev

Проверка

Убедись, что в config/settings.py домен добавлен в ALLOWED_HOSTS:

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'hatchling-causal-doornail.ngrok-free.dev']








# Тестовые данные (фикстуры)

Наборы данных для локальной разработки и ручного тестирования. Заполняют базу пользователями, новостями, мероприятиями, симптомами, карточками пациентов и справочными материалами на трёх языках (RU/KY/EN, где применимо).


## Загрузка

Сначала миграции (на чистой базе):

```bash
python manage.py migrate
```
Создайте группы строго по порядку.Чтобы права доступа не перепутались.
```bash
python manage.py setup_moderator_group
python manage.py setup_manager_group
```

Затем фикстуры — **строго в этом порядке**, из-за связей между моделями (`patients` ссылается на `accounts`, `resources` ссылается на `patients.Symptom`):

```bash
python manage.py loaddata accounts_fixtures
python manage.py loaddata news_fixtures
python manage.py loaddata events_fixtures
python manage.py loaddata patients_fixtures
python manage.py loaddata resources_fixtures
```

## Тестовые пользователи

Пароль у всех одинаковый: **`Testpass123!`**. Вход по **email**, не по username.

| Роль | Email |
|---|---|
| Админ | `admin@palliativ.kg` |
| Менеджер | `manager@palliativ.kg` |
| Модератор | `moderator@palliativ.kg` |
| Врач | `doctor1@palliativ.kg`, `doctor2@palliativ.kg` |
| Пациент | `patient1@palliativ.kg` … `patient5@palliativ.kg` |

Админка: `/admin/`, вход теми же данными (`admin@palliativ.kg`).

## Что внутри

- **accounts_fixtures.json** — 10 пользователей всех ролей + `DoctorProfile` (2) + `PatientProfile` (5)
- **news_fixtures.json** — 3 категории, 6 новостей
- **events_fixtures.json** — 7 мероприятий
- **patients_fixtures.json** — 5 симптомов, 4 карточки пациента (диагноз, препараты, симптомы, врач)
- **resources_fixtures.json** — 7 справочных материалов


## Повторная генерация / очистка

Очистить базу перед загрузкой заново:

```bash
python manage.py flush
```
Удалит все данные, структуру таблиц не тронет — миграции применять заново не нужно.

Создайте группы строго по порядку.Чтобы права доступа не перепутались.
```bash
python manage.py setup_moderator_group
python manage.py setup_manager_group
```

















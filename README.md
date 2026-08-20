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
Для Ubuntu/Debian:

sudo apt update
sudo apt install -y python3-venv libpq-dev postgresql postgresql-contrib
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
Разработка
Основная ветка разработки:

dev
Перед началом работы рекомендуется:

git checkout dev
git pull origin dev
Для новых задач создавайте отдельные feature-ветки:

git checkout -b feature/task-name
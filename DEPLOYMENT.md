DEPLOYMENT.md
Сервер
IP: 37.139.26.171
ОС: Ubuntu 24.04 LTS
Пользователь для работы: deploy (обычный пользователь с правами sudo, вход только по SSH-ключу)
Root по SSH: заблокирован (PermitRootLogin no)
Firewall: включён (ufw), открыты порты 22 (SSH) и 80 (HTTP)
Доступ к серверу

Вход осуществляется по SSH-ключу, без пароля:

ssh deploy@37.139.26.171

Пароль пользователя deploy используется только для команд с sudo на самом сервере и никому кроме администратора сервера не сообщается.

Список участников с доступом
Имя	Публичный ключ добавлен	Дата
Ramazan Toichuev	✅	27.09.2026
atai-palliativ	✅	28.09.2026
(участник 3)	⬜	
(участник 4)	⬜	
(участник 5)	⬜	
(участник 6)	⬜	
Как добавить нового участника
Новый участник генерирует SSH-ключ у себя на компьютере (если его ещё нет):
   ssh-keygen -t ed25519 -C "имя_человека"
Показывает свой публичный ключ:
Windows (PowerShell): type $env:USERPROFILE\.ssh\id_ed25519.pub
Mac/Linux: cat ~/.ssh/id_ed25519.pub
Отправляет получившуюся строку (вида ssh-ed25519 AAAA... имя) администратору сервера личным сообщением, не в общий чат.
Администратор сервера заходит под deploy и добавляет ключ:
   echo 'ssh-ed25519 AAAA... имя' >> ~/.ssh/authorized_keys
Новый участник проверяет вход:
   ssh deploy@37.139.26.171

Вход должен пройти без запроса пароля. 6. Администратор отмечает участника в таблице выше.

Как удалить доступ участника
Открыть файл ~/.ssh/authorized_keys под deploy:
   nano ~/.ssh/authorized_keys
Удалить строку с ключом нужного человека.
Сохранить (Ctrl+O, Enter) и выйти (Ctrl+X).
Обновить таблицу в этом файле.
Docker и Docker Compose

Установлены на сервере под пользователем deploy, доступны без sudo (пользователь в группе docker).

Команда установки (официальный скрипт Docker):

curl -fsSL https://get.docker.com | sh

Ставит Docker Engine, containerd, Docker CLI и плагин docker-compose-plugin (команда docker compose) одним шагом.

Версии на момент установки:

docker --version

→ Docker Engine 29.8.1 (Community)

docker compose version

→ уточнить актуальный вывод на сервере (плагин ставится вместе с Docker Engine из того же скрипта)

Проверка, что всё работает:

docker run hello-world

Должно вывести «Hello from Docker!».

Структура образа приложения (Dockerfile)

Базовый образ: python:3.13-slim.

Шаги сборки:

Отключение записи .pyc-файлов и буферизации вывода Python (PYTHONDONTWRITEBYTECODE, PYTHONUNBUFFERED).
Установка системных пакетов, нужных для сборки: build-essential, libpq-dev (для PostgreSQL-драйвера), curl, ghostscript.
Установка Python-зависимостей из requirements.txt.
Копирование кода проекта в /app.
entrypoint.sh делается исполняемым и используется как ENTRYPOINT.
По умолчанию (CMD) контейнер запускает python manage.py runserver 0.0.0.0:8000, порт 8000 открыт (EXPOSE).
docker-compose.yml — сервисы

Было до тикета 90 (из PR Рамазана):

web — сборка из Dockerfile, порт 8000:8000 наружу, читает .env, зависит от db и redis (ждёт их healthcheck).
huey — та же сборка, обработчик фоновых задач (python manage.py run_huey), тоже читает .env, зависит от db и redis.

Добавлено в тикете 90:

db — образ postgres:18.4-alpine, том postgres_data для данных, переменные POSTGRES_DB/USER/PASSWORD из .env, healthcheck через pg_isready.
redis — образ redis:8.10-alpine, healthcheck через redis-cli ping.

Важно: у db и redis нет публикации портов наружу (ports: не указан) — они доступны только другим сервисам внутри Docker-сети по именам db и redis, снаружи сервера не видны. Так надёжнее: ufw не может заблокировать порты, которые Docker публикует через ports:, поэтому единственный правильный способ не открывать их наружу — просто не публиковать.

Сервисы db и redis пока не запущены (docker compose up для них — задача следующего тикета).

Переменные окружения (.env)

Приложение и Docker-сервисы получают настройки через файл .env в корне проекта (не коммитится в Git, есть в .gitignore). Шаблон — .env.example.

Две группы переменных отвечают за базу данных, потому что их читают разные потребители:

POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD (в docker-compose.yml, подставляются из DB_NAME/DB_USER/DB_PASSWORD в .env) — нужны официальному образу postgres, чтобы при первом запуске создать базу и пользователя.
DB_URL — читается Django через django-environ (env.db('DB_URL') в config/settings.py), формат: postgres://пользователь:пароль@db:5432/имя_базы. Хост — db, это имя сервиса в Docker-сети, не localhost.

Оба должны описывать одну и ту же базу согласованными значениями.

REDIS_URL — аналогично, читается Django/Huey напрямую, формат redis://redis:6379/3, хост redis — имя сервиса.

Сервисы web и huey в docker-compose.yml подключают .env целиком через env_file: .env, так что все переменные из файла становятся доступны внутри контейнера автоматически, отдельно прокидывать каждую не нужно.

Firewall (ufw)

Открытые порты:

22 (OpenSSH) — доступ по SSH
80 (HTTP) — сайт

Проверка статуса:

sudo ufw status
Сайт (ещё не развёрнут)

postgres и redis описаны в docker-compose.yml, но намеренно не запущены — запуск всех сервисов вместе (web, huey, db, redis) относится к отдельному тикету.

Когда до этого дойдёт очередь, ожидаемые шаги:

git clone -b main https://github.com/ВАШ_РЕПО.git ~/site
cd ~/site
cp .env.example .env   # и заполнить реальными значениями
sudo ufw allow 80/tcp  # если веб-сервис должен быть доступен снаружи
docker compose up -d --build
docker ps

Сайт будет доступен по адресу: http://37.139.26.171

(Домен и HTTPS будут добавлены отдельно, когда появится доменное имя.)
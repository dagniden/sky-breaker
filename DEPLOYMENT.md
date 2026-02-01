# Инструкция по деплою на Debian сервер

## Предварительные требования

На сервере должны быть установлены:
- Python 3.11+ (проект совместим с Python 3.11, 3.12, 3.13)
- PostgreSQL
- Nginx
- Git
- Poetry

## Шаг 1: Установка зависимостей на сервере

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11+ (обычно уже установлен в Debian)
sudo apt install python3 python3-venv python3-pip -y

# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Установка Nginx
sudo apt install nginx -y

# Установка Git
sudo apt install git -y

# Установка Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Шаг 2: Настройка PostgreSQL

```bash
# Переключиться на пользователя postgres
sudo -u postgres psql

# В консоли PostgreSQL выполнить:
CREATE DATABASE skybreaker;
CREATE USER skybreaker_user WITH PASSWORD 'ваш_пароль';
ALTER ROLE skybreaker_user SET client_encoding TO 'utf8';
ALTER ROLE skybreaker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE skybreaker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE skybreaker TO skybreaker_user;

# Подключиться к базе данных
\c skybreaker

# Дать права на схему public (критично для миграций!)
GRANT ALL ON SCHEMA public TO skybreaker_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO skybreaker_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO skybreaker_user;

# Для PostgreSQL 15+ также установить владельца схемы
ALTER SCHEMA public OWNER TO skybreaker_user;

\q
```

**Важно:** Без прав на схему `public` миграции Django не смогут создать таблицы!

## Шаг 3: Клонирование проекта

```bash
# Перейти в домашнюю директорию
cd ~

# Клонировать репозиторий
git clone https://github.com/dagniden/sky-breaker.git
cd sky-breaker
```

**Примечание:** Проект будет находиться в `~/sky-breaker` (например, `/home/username/sky-breaker`)

## Шаг 4: Настройка окружения

```bash
# Скопировать .env.example в .env
cp .env.example .env

# Отредактировать .env с настройками для production
nano .env
```

Пример .env для сервера:
```
SECRET_KEY=сгенерируйте-новый-секретный-ключ
DEBUG=False
ALLOWED_HOSTS=ваш-домен.com,www.ваш-домен.com

DB_NAME=skybreaker
DB_USER=skybreaker_user
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
```

Для генерации SECRET_KEY (после установки зависимостей):
```bash
# Вариант 1: Через Poetry (после poetry install)
poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Вариант 2: Без Django
python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#\$%^&*(-_=+)') for i in range(50)))"
```

## Шаг 5: Установка зависимостей и настройка Django

```bash
# Установить зависимости через Poetry (без dev-зависимостей)
poetry install --without dev

# Применить миграции
poetry run python manage.py migrate

# Импортировать статьи из Markdown файлов
poetry run python manage.py import_articles

# Собрать статические файлы
poetry run python manage.py collectstatic --noinput

# Создать суперпользователя
poetry run python manage.py createsuperuser
```

## Шаг 6: Настройка Gunicorn

```bash
# Создать systemd service файл
sudo nano /etc/systemd/system/skybreaker.service
```

Содержимое файла (замените `username` на ваше имя пользователя):
```ini
[Unit]
Description=Sky Breaker Gunicorn daemon
After=network.target

[Service]
User=username
Group=www-data
WorkingDirectory=/home/username/sky-breaker
Environment="PATH=/home/username/sky-breaker/.venv/bin"
ExecStart=/home/username/.local/bin/poetry run gunicorn --workers 3 --bind unix:/home/username/sky-breaker/skybreaker.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Важно:**
- Замените `username` на ваше реальное имя пользователя (узнать можно командой `whoami`)
- ExecStart должен быть в одной строке без переносов!

```bash
# Перезагрузить systemd после создания файла
sudo systemctl daemon-reload

# Запустить и включить сервис
sudo systemctl start skybreaker
sudo systemctl enable skybreaker

# Проверить статус
sudo systemctl status skybreaker
```

## Шаг 7: Настройка Nginx

```bash
# Создать конфигурационный файл
sudo nano /etc/nginx/sites-available/skybreaker
```

Содержимое файла (замените `username` и `ваш-домен.com`):
```nginx
server {
    listen 80;
    server_name ваш-домен.com www.ваш-домен.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/username/sky-breaker/staticfiles/;
    }

    location /media/ {
        alias /home/username/sky-breaker/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/username/sky-breaker/skybreaker.sock;
    }
}
```

**Важно:** Замените `username` на ваше имя пользователя

```bash
# Удалить старые конфигурации (если были)
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/sky-breaker  # если есть старые

# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/skybreaker /etc/nginx/sites-enabled/

# Дать Nginx доступ к домашней директории (критично!)
sudo usermod -a -G $(whoami) www-data
chmod 710 ~

# Проверить конфигурацию Nginx
sudo nginx -t

# Перезапустить Nginx
sudo systemctl restart nginx
```

**Важно:** Без прав доступа к домашней директории Nginx не сможет подключиться к сокету!

## Шаг 8: Настройка SSL (опционально, но рекомендуется)

```bash
# Установить Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить SSL сертификат
sudo certbot --nginx -d ваш-домен.com -d www.ваш-домен.com

# Certbot автоматически настроит HTTPS и перенаправление
```

## Обновление проекта

Когда нужно обновить код на сервере:

```bash
cd ~/sky-breaker

# Получить последние изменения
git pull origin main

# Обновить зависимости (если изменились)
poetry install --without dev

# Применить новые миграции (если есть)
poetry run python manage.py migrate

# Импортировать статьи (если обновились MD файлы)
poetry run python manage.py import_articles

# Собрать статические файлы
poetry run python manage.py collectstatic --noinput

# Перезапустить Gunicorn
sudo systemctl restart skybreaker
```

## Проверка логов

```bash
# Логи Gunicorn
sudo journalctl -u skybreaker -f

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Готово!

Ваш проект должен быть доступен по адресу:
- http://ваш-домен.com/sleepy/ - список статей
- http://ваш-домен.com/admin/ - панель администратора

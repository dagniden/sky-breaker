# Sky Breaker

Веб-приложение на Django для публикации курса Sleepy - 30-дневного курса по улучшению сна.

## Возможности

- Публикация статей курса из Markdown файлов
- Автоматическая конвертация Markdown в HTML
- Поддержка wiki-ссылок между статьями
- Навигация между днями курса
- Административная панель для управления контентом

## Технологии

- Python 3.13
- Django 5.2
- PostgreSQL
- Poetry для управления зависимостями
- Markdown для контента

## Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/sky-breaker.git
cd sky-breaker
```

2. Установите зависимости:
```bash
poetry install
```

3. Настройте базу данных в файле .env (скопируйте из .env.example)

4. Примените миграции:
```bash
poetry run python manage.py migrate
```

5. Импортируйте статьи:
```bash
poetry run python manage.py import_articles
```

6. Создайте суперпользователя:
```bash
poetry run python manage.py createsuperuser
```

7. Запустите сервер разработки:
```bash
poetry run python manage.py runserver
```

Откройте http://localhost:8000/sleepy/ для просмотра статей.

## Деплой на сервер

См. подробную инструкцию в файле [DEPLOYMENT.md](DEPLOYMENT.md)

## Структура проекта

- `config/` - настройки Django проекта
- `sleepy/` - приложение для управления статьями курса
- `data/Sleepy/` - Markdown файлы со статьями
- `manage.py` - Django management script

## Лицензия

Все права защищены.

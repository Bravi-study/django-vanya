# django-vanya

Учебный проект на Django для подготовки к техническому собеседованию. Приложение показывает классический серверный Django-подход: модели, формы, class-based views, аутентификацию, админку, тесты, небольшой JSON API и запуск через Docker.

## Что внутри

- Трекер задач с ролями владельца и исполнителя
- SQLite по умолчанию, чтобы старт был максимально простым
- Поясняющие комментарии в коде на русском языке
- Django admin с настройками для быстрой навигации
- DRF API для задач
- Тесты на модели, формы, views, auth и API
- Dockerfile для сборки образа и запуска контейнера

## Ключевые маршруты

- `/` — главная страница с кратким обзором проекта
- `/tasks/` — список задач текущего пользователя
- `/accounts/login/` — вход
- `/accounts/signup/` — регистрация
- `/admin/` — админка Django
- `/api/tasks/` — JSON API

## Локальный запуск

Проект использует `uv` и `pyproject.toml` как основной способ управления зависимостями.

```bash
uv sync
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

После этого приложение будет доступно на `http://127.0.0.1:8000/`.

## Полезные команды

```bash
.venv/bin/python manage.py test tasks
.venv/bin/python manage.py check
.venv/bin/python manage.py shell
```

## Запуск через Docker

Сборка образа:

```bash
docker build -t django-vanya .
```

Запуск контейнера:

```bash
docker run --rm \
	-p 8000:8000 \
	-e DJANGO_SECRET_KEY='change-me-for-real-projects' \
	-v django-vanya-data:/data \
	django-vanya
```

Что делает контейнер при старте:

- применяет миграции
- собирает static-файлы
- запускает Gunicorn на `0.0.0.0:8000`

SQLite-файл в Docker хранится в `/data/db.sqlite3`, поэтому для сохранения данных между перезапусками используется volume `django-vanya-data`.

## Переменные окружения

- `DJANGO_SECRET_KEY` — секретный ключ Django
- `DJANGO_DEBUG` — `1` для локальной отладки, `0` для Docker и более реалистичного режима
- `DJANGO_ALLOWED_HOSTS` — список хостов через запятую
- `SQLITE_NAME` — путь к SQLite-базе или имя файла относительно корня проекта

## Что обсуждать на собеседовании по этому проекту

- Почему для CRUD-приложения удобно начинать с generic class-based views
- Как `select_related` и `prefetch_related` убирают лишние запросы
- Чем `ModelForm` полезен по сравнению с ручной обработкой `POST`
- Как устроены стандартные auth views Django и как их расширять
- Почему админка хорошо подходит для внутренних инструментов и MVP
- Где в API проходит граница между авторизацией и объектными правами доступа
- Зачем Docker нужен даже для простого pet-проекта

## Где SQLite отличается от PostgreSQL

SQLite здесь выбран ради простого старта, но на собеседовании полезно отдельно проговорить отличия:

- Поиск по `icontains` и сортировка по строкам зависят от коллаций SQLite и обычно беднее, чем в PostgreSQL.
- Конкурентные записи в SQLite масштабируются хуже. Для одного разработчика это удобно, для нагруженного production почти всегда выбирают PostgreSQL.
- PostgreSQL даёт richer features: полнотекстовый поиск, более сильные индексы, `JSONB`, `ArrayField`, `citext`, расширения и более предсказуемый planner.
- В этом проекте сознательно использованы переносимые возможности Django ORM, чтобы код одинаково хорошо читался и на SQLite, и на PostgreSQL.

## Структура проекта

```text
config/          Django settings, root urls, ASGI, WSGI
tasks/           Модели, формы, views, admin, API и тесты
templates/       Базовый шаблон, страницы задач и auth-шаблоны
Dockerfile       Сборка контейнера
entrypoint.sh    Миграции, static и запуск внутри Docker
```

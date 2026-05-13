# FastAPI Notes Service

FastAPI-сервис для управления пользовательскими заметками с JWT-авторизацией, refresh-token rotation через Redis и асинхронной обработкой CRUD-операций заметок через RabbitMQ RPC.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy async + asyncpg
- PostgreSQL 16
- Alembic
- Redis
- RabbitMQ
- aio-pika
- PyJWT
- pwdlib / Argon2
- Docker Compose
- Ruff

## Архитектура

Авторизация выполняется в API-сервисе напрямую:

```text
HTTP auth request -> FastAPI -> PostgreSQL / Redis -> HTTP response
```

Операции над заметками выполняются через RabbitMQ:

```text
HTTP /notes -> FastAPI -> RabbitMQ -> notes_worker -> PostgreSQL -> RabbitMQ -> FastAPI -> HTTP response
```

API-сервис не выполняет CRUD заметок напрямую. Он отправляет RPC-запрос в очередь `notes_rpc`, а `notes_worker` обрабатывает команду и возвращает ответ.

## Быстрый Старт

1. Создайте `.env` из примера:

```bash
cp .env.example .env
```

2. Запустите сервисы:

```bash
docker compose up --build
```

3. Откройте документацию API:

```text
http://127.0.0.1:8000/docs
```

RabbitMQ Management UI:

```text
http://127.0.0.1:15672
```

Логин и пароль берутся из `.env`:

```env
RABBITMQ__USER=guest
RABBITMQ__PASSWORD=guest
```

## Сервисы Docker Compose

- `auth` - FastAPI API-сервис.
- `notes_worker` - worker, который обрабатывает CRUD заметок из RabbitMQ.
- `auth_database` - PostgreSQL.
- `redis` - хранение активных refresh-токенов.
- `rabbitmq` - брокер сообщений для RPC по заметкам.

## Переменные Окружения

Все необходимые переменные перечислены в `.env.example`.

Для запуска внутри Docker Compose:

```env
POSTGRES__HOST=auth_database
REDIS__HOST=redis
RABBITMQ__HOST=rabbitmq
```

Если запускаете Alembic локально с хоста, используйте:

```env
POSTGRES__HOST=localhost
```

## Миграции

В контейнере миграции запускаются автоматически через `entrypoint.sh`:

```bash
alembic upgrade head
```

Создать новую миграцию локально:

```bash
alembic revision --autogenerate -m "migration name"
```

Применить миграции локально:

```bash
alembic upgrade head
```

## Авторизация

### Регистрация

```http
POST /
```

Body:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Ответ содержит пользователя, `access_token` и `refresh_token`. Также токены кладутся в `HttpOnly` cookies.

### Логин

```http
POST /login
```

Body:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Обновление Токенов

```http
POST /refresh
```

Refresh token берётся из `HttpOnly` cookie `refresh_token`. Для Postman/CLI можно передать его в body:

```json
{
  "refresh_token": "..."
}
```

При refresh выполняется rotation:

- старый refresh token удаляется из Redis;
- создаётся новая пара `access_token` + `refresh_token`;
- новая refresh-сессия сохраняется в Redis;
- cookies обновляются.

### Logout

```http
POST /logout
```

Logout удаляет refresh token из Redis и очищает auth cookies.

## Заметки

Для endpoints заметок нужен `access_token`. Он может быть передан:

- через `HttpOnly` cookie `access_token`;
- через заголовок `Authorization: Bearer <access_token>`.

### Создать Заметку

```http
POST /notes/
```

Body:

```json
{
  "title": "Первая заметка",
  "content": "Текст заметки"
}
```

### Получить Список Заметок

```http
GET /notes/?page=1&per_page=20&search=test&is_archived=false
```

Query-параметры:

- `page` - номер страницы.
- `per_page` - количество заметок на странице.
- `search` - поиск по `title` и `content`.
- `is_archived` - фильтр по архиву.

### Получить Заметку По ID

```http
GET /notes/{note_id}
```

### Обновить Заметку

```http
PATCH /notes/{note_id}
```

Body:

```json
{
  "title": "Новое название",
  "content": "Новый текст"
}
```

### Архивировать Заметку

```http
POST /notes/{note_id}/archive
```

### Удалить Заметку

```http
DELETE /notes/{note_id}
```

Удаление физически удаляет запись из базы.

## RabbitMQ RPC

API отправляет сообщения в очередь:

```env
RABBITMQ__NOTES_QUEUE=notes_rpc
```

Формат запроса:

```json
{
  "action": "create_note",
  "user_id": 1,
  "payload": {
    "title": "Note",
    "content": "Text"
  }
}
```

Формат успешного ответа:

```json
{
  "ok": true,
  "data": {}
}
```

Формат ошибки:

```json
{
  "ok": false,
  "status_code": 404,
  "error": "Note not found"
}
```

## Полезные Команды

Запуск:

```bash
docker compose up --build
```

Остановка:

```bash
docker compose down
```

Остановка с удалением volume:

```bash
docker compose down -v
```

Логи API:

```bash
docker compose logs -f auth
```

Логи worker:

```bash
docker compose logs -f notes_worker
```

Форматирование и автоисправления:

```bash
ruff check app --fix
ruff format app
```

Проверка импортов и синтаксиса:

```bash
python -m compileall app
```

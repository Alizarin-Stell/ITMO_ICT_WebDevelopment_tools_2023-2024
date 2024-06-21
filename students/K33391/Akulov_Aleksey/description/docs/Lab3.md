# Отчет по лабораторной работе №3

Выполнил: Акулов Алексей, K33391

#### Цель работы:

Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

## Задание 1

### Текст задания:

Docker — это платформа для разработки, доставки и запуска приложений в контейнерах.
Контейнеры позволяют упаковать приложение и все его зависимости в единый образ,
который можно запускать на любой системе, поддерживающей Docker, что обеспечивает консистентность среды выполнения и упрощает развертывание.
Docker помогает ускорить разработку, повысить гибкость и масштабируемость приложений. Материалы


#### Dockerfile

```
FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --root-user-action=ignore -r /app/requirements.txt

COPY . .

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Задание 2

### Текст задания:

Эндпоинт в FastAPI для вызова парсера**:
Необходимо добавить в FastAPI приложение ендпоинт,
который будет принимать запросы с URL для парсинга от клиента,
отправлять запрос парсеру (запущенному в отдельном контейнере) и возвращать ответ с результатом клиенту.

#### Dockerfile

```
FROM python:3.11

WORKDIR /parser

COPY requirements.txt .

RUN pip install --root-user-action=ignore -r /parser/requirements.txt

COPY . .

CMD [ "uvicorn", "parser:app", "--host", "0.0.0.0", "--port", "8081"]
```

Дальше необходимо убедиться, что все работает, запустив контейнеры

#### docker-compose

```
version: '3.11'

services:
  postgres:
    image: postgres
    container_name: postgres_db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=12345
      - POSTGRES_DB=money_db
    ports:
      - "5434:5433"

  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    env_file:
      - app/.env
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  parser:
    build:
      context: ./parser
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    depends_on:
      - postgres
      - app
```

Здесь необходимо также правильно прописать досутпы к базе данных в окружениях:
у нас сервер теперь postgres, порт 5432 и пароль, который существует у постгреса
# Logistics Backend

Система управления логистикой / Доставкой — учебный проект Backend 2026.

## Стек

- FastAPI
- SQLAlchemy 2.0 async
- PostgreSQL 16
- Alembic
- fastapi-users (JWT)
- Docker + Mailpit

## Запуск

```bash
docker compose up -d
uv sync
cd app && python main.py
```

Swagger: http://localhost:8000/docs  
Mailpit: http://localhost:8025

FROM python:3.12-slim

WORKDIR /app

COPY src/backend/pyproject.toml .
COPY src/backend/alembic.ini .
COPY src/backend/alembic ./alembic
COPY src/backend/app ./app
COPY docs ./docs

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

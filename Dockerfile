FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    DJANGO_DEBUG=0 \
    DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost \
    SQLITE_NAME=/data/db.sqlite3

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app --home /home/app app \
    && mkdir -p /data

RUN pip install --no-cache-dir --upgrade pip "uv>=0.7,<0.8"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

RUN chmod +x /app/entrypoint.sh \
    && chown -R app:app /app /data

USER app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/.venv/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]

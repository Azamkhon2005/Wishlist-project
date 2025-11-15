FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY ./app ./app
COPY ./tests ./tests

ENV PYTHONPATH=/app

RUN python -m pytest

FROM python:3.11.9-slim-bookworm

RUN adduser --system --group appuser

ENV PYTHONUSERBASE=/home/appuser/.local

ENV PATH=${PYTHONUSERBASE}/bin:${PATH}

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=appuser:appuser ./app ./app

RUN mkdir -p /app/app/data && chown -R appuser:appuser /app/app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

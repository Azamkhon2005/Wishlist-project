FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
COPY ./app ./app
COPY ./tests ./tests
ENV PYTHONPATH=/app
RUN python -m pytest -q

FROM python:3.11-slim

WORKDIR /code

RUN useradd -m appuser

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY --from=build /app/app /code/app

RUN mkdir -p /code/app/data
RUN chown -R appuser:appuser /code/app

EXPOSE 8000
USER appuser
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

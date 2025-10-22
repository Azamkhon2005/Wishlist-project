# ADR-001: Стандартизированный формат ошибок RFC 7807 + correlation_id
Дата: 2025-10-22
Статус: Accepted

## Context
- В проекте ранее использовался кастомный формат ошибок и временный шаблонный эндпоинт `/items` — удалены.
- Требуется единый и безопасный формат ошибок (NFR-07), без утечки внутренних деталей.
- Для трассировки инцидентов нужен `correlation_id`.
- В FastAPI/Starlette ошибки могут подниматься как `fastapi.HTTPException`, `starlette.exceptions.HTTPException` (например, при отсутствии заголовка `X-API-Key`) и `RequestValidationError` (валидация запроса).

## Decision
- Используем формат RFC 7807: поля `type`, `title`, `status`, `detail`, `correlation_id`.
- Генерируем `correlation_id` (UUID) и возвращаем также в заголовке `X-Correlation-ID`.
- Обрабатываем и приводим к RFC7807 все исключения:
  - Доменные `ApiError` → RFC7807 с `status` из исключения.
  - `fastapi.HTTPException` → RFC7807.
  - `starlette.exceptions.HTTPException` → RFC7807 (важно для кейса отсутствующего `X-API-Key` → 403).
  - `RequestValidationError` → RFC7807 с `422 Validation error`, без деталей внутренней структуры Pydantic.
- Карта типов проблем:
  - 401: `urn:problem:unauthorized`
  - 403: `urn:problem:forbidden`
  - 404: `urn:problem:not-found`
  - 422: `urn:problem:validation-error`
  - 429: `urn:problem:rate-limit`
  - иначе: `about:blank`

## Consequences
- Плюсы: единообразие, безопасность (нет stack trace/внутренних путей), трассировка по `correlation_id`.
- Минусы: рефакторинг тестов и обработчиков.
- Риски: разработчики могут нечаянно писать чувствительные данные в `detail`; смягчение — ревью и линтеры.

## Alternatives
- Оставить произвольный формат ошибок — хуже DX, нарушает NFR-07.
- Использовать внешнюю библиотеку для RFC7807 — избыточно для учебного проекта.

## Links
- NFR: NFR-07 (Безопасная обработка ошибок)
- Threat Model: R6 (Раскрытие внутренних деталей)
- Реализация: `app/main.py` (функция `problem()`, обработчики для `ApiError`, `fastapi.HTTPException`, `starlette.HTTPException`, `RequestValidationError`)
- Tests:
  - `tests/test_errors.py::test_rfc7807_invalid_api_key_unauthorized`
  - `tests/test_errors.py::test_rfc7807_missing_api_key_forbidden`
  - `tests/test_errors.py::test_rfc7807_not_found_wish`
  - `tests/test_errors.py::test_rfc7807_validation_error_on_register`

# ADR-001: Стандартизированный формат ошибок RFC 7807/9457 (Problem Details) + correlation_id
Дата: 2025-10-20
Статус: Accepted

## Context
- В проекте ранее использовался кастомный формат ошибок и временные эндпоинты `/items` — удалены.
- Требуется единый и безопасный формат ошибок (NFR-07), без утечки внутренних деталей.
- Для трассировки инцидентов нужен `correlation_id`.
- В FastAPI/Starlette ошибки могут подниматься как `fastapi.HTTPException`, `starlette.exceptions.HTTPException` (например, при отсутствии заголовка `X-API-Key`) и `RequestValidationError` (валидация запроса).

## Decision
- Используем формат Problem Details (RFC 9457, ранее RFC 7807): `type`, `title`, `status`, `detail`, `correlation_id`.
- Генерируем `correlation_id` (UUID) и возвращаем также в заголовке `X-Correlation-ID`.
- Обрабатываем и приводим к Problem Details все исключения:
  - Доменные `ApiError` → Problem Details с `status` из исключения.
  - `fastapi.HTTPException` → Problem Details.
  - `starlette.exceptions.HTTPException` → Problem Details (важно для кейса отсутствующего `X-API-Key` → 403).
  - `RequestValidationError` → Problem Details с `422 Validation error`, без внутренних деталей Pydantic.
- Карта типов проблем:
  - 401: `urn:problem:unauthorized`
  - 403: `urn:problem:forbidden`
  - 404: `urn:problem:not-found`
  - 422: `urn:problem:validation-error`
  - 429: `urn:problem:rate-limit`
  - иначе: `about:blank`

## Consequences
- Плюсы: единообразие, безопасность (нет stack trace/внутренних путей), трассировка по `correlation_id`.
- Минусы: небольшой рефакторинг тестов и обработчиков.
- Риски: разработчики могут нечаянно писать чувствительные данные в `detail`; смягчение — ревью и линтеры.

## Alternatives
- Оставить произвольный формат ошибок — хуже DX, нарушает NFR-07.
- Внешняя библиотека — избыточно для учебного проекта.

## Links
- NFR: NFR-07 (Безопасная обработка ошибок)
- Threat Model: R6 (Раскрытие внутренних деталей)
- Реализация: `app/main.py` (функция `problem()`, обработчики для `ApiError`, `fastapi.HTTPException`, `starlette.HTTPException`, `RequestValidationError`)
- Tests:
  - `tests/test_errors.py::test_rfc7807_missing_api_key_forbidden`
  - `tests/test_errors.py::test_rfc7807_not_found_wish`

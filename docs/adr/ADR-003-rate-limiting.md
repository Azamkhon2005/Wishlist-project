# ADR-003: Rate Limiting (регистрация и API с X-API-Key)
Дата: 2025-10-22
Статус: Accepted

## Context
- Необходимо снизить риски brute-force и DoS (R1, R11).
- NFR-02: лимиты — POST `/api/users/` ≤ 5 запросов/мин с одного IP; все `/api/*` с `X-API-Key` ≤ 100 запросов/мин по ключу (если ключа нет — по IP).
- В учебном окружении нет внешнего RL (ingress/gateway/Redis), значит вводим базовый RL на уровне приложения.

## Decision
- Добавляем in-memory middleware со скользящим окном 60 секунд.
- Определение источника IP: `X-Forwarded-For` (первый из списка), иначе `request.client.host`.
- Ключи учёта:
  - Регистрация: `reg:{ip}`, лимит=5/мин (только POST `/api/users/`).
  - Остальные `/api/*`: если есть `X-API-Key` → `auth:{api_key}`, иначе `auth-ip:{ip}`, лимит=100/мин.
- При превышении возвращаем 429 в RFC7807-формате (через общий `problem()`).
- На проде дополнить RL на edge (ingress/gateway) или вынести сторедж в Redis.

## Consequences
- Плюсы: блокируем базовые сценарии brute-force/DoS на уровне приложения, соответствуем NFR-02.
- Минусы: in-memory не масштабируется горизонтально; персистентность отсутствует.
- Компромисс: простая реализация для учебного проекта, при масштабировании — миграция на Redis или edge RL.

## Alternatives
- Только gateway/ingress RL — лучше для прод, но недоступно в учебной среде.
- Redis + token/leaky bucket — более надёжно и масштабируемо, но сложнее в этой итерации.

## Links
- NFR: NFR-02
- Threat Model: R1 (брутфорс регистрации), R11 (DoS)
- Реализация: `app/main.py` (`RateLimitMiddleware`, учёт `X-Forwarded-For`, интеграция с RFC7807)
- Tests:
  - `tests/test_rate_limit.py::test_registration_rate_limit_5_per_minute`

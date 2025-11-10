import sys
from pathlib import Path

import pytest

from app.main import RateLimitMiddleware

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def disable_rate_limit_for_tests(monkeypatch, request):
    if "rate_limit" in request.keywords:
        RateLimitMiddleware.storage.clear()
        yield
    else:
        monkeypatch.setattr(RateLimitMiddleware, "_allow", lambda *args, **kwargs: True)
        yield

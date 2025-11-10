# app/custom_routing.py

import json
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.datastructures import FormData


class _JSONRequest(Request):
    async def json(self) -> any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body, parse_float=str)
        return self._json

    async def form(self) -> FormData:
        if not hasattr(self, "_form"):
            content_type = self.headers.get("content-type", "")
            if "application/json" in content_type:
                return FormData()
            return await super().form()
        return self._form


class SecureJsonRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            safe_request = _JSONRequest(request.scope, request.receive)
            return await original_route_handler(safe_request)

        return custom_route_handler

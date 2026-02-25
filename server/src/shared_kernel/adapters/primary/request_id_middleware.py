import logging
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Reads X-Request-ID from the incoming request (or generates a UUID) and
    echoes it in the response. Stores it in a ContextVar so that all log
    records emitted within the request carry the same request_id field."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = _request_id_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            _request_id_var.reset(token)


class RequestIdFilter(logging.Filter):
    """Logging filter that injects the current request_id into every log record.

    Install on the root logger so all loggers (including third-party) carry
    the field. JsonFormatter will then include it in structured output via
    the extra-field merge."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get()
        return True

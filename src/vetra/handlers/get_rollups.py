from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from vetra import ddb
from vetra.auth import get_claims
from vetra.config import get_settings
from vetra.errors import ForbiddenError, UnauthorizedError, ValidationError
from vetra.logging import logger, tracer, with_correlation_id

settings = get_settings()


def _parse_dates(params: dict[str, str]) -> tuple[str, str]:
    start = params.get("from")
    end = params.get("to")
    if not start or not end:
        raise ValidationError("from and to query parameters are required")
    try:
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)
    except ValueError as exc:
        raise ValidationError("Dates must be ISO format YYYY-MM-DD") from exc
    return start, end


def _build_response(status: int, body: Any) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, _context):
    with_correlation_id(event.get("headers"))
    try:
        claims = get_claims(event)
        params = event.get("queryStringParameters") or {}
        start, end = _parse_dates(params)
        rollups = ddb.query_rollups(claims, start, end)
        device_id = params.get("deviceId")
        events = []
        if device_id:
            events = ddb.query_events_by_device(device_id)
        return _build_response(200, {"rollups": rollups, "events": events})
    except ValidationError as exc:
        return _build_response(400, {"message": str(exc)})
    except UnauthorizedError:
        return _build_response(401, {"message": "Unauthorized"})
    except ForbiddenError:
        return _build_response(403, {"message": "Forbidden"})
    except Exception:
        logger.exception("Unhandled error in get_rollups")
        return _build_response(500, {"message": "Internal server error"})

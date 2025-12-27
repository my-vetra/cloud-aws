from __future__ import annotations

import base64
import json

from aws_lambda_powertools.metrics import MetricUnit

from vetra import ddb
from vetra.auth import get_claims
from vetra.config import get_settings
from vetra.errors import ConflictError, ForbiddenError, PayloadTooLargeError, UnauthorizedError, ValidationError
from vetra.logging import logger, metrics, tracer, with_correlation_id
from vetra.validation import enforce_max_body_size, parse_json_body, validate_event_payload

settings = get_settings()


def _decode_body(event_body: str, is_base64: bool) -> str:
    if is_base64:
        return base64.b64decode(event_body).decode("utf-8")
    return event_body


def _build_response(status: int, body: dict[str, object]) -> dict:
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
        raw_body = event.get("body") or ""
        is_base64 = bool(event.get("isBase64Encoded"))
        decoded_body = _decode_body(raw_body, is_base64)
        enforce_max_body_size(decoded_body, settings.max_body_bytes)
        payload = parse_json_body(decoded_body)
        validate_event_payload(payload)
        idempotency_key = None
        headers = event.get("headers") or {}
        if headers:
            idempotency_key = headers.get("Idempotency-Key") or headers.get("idempotency-key")
        result = ddb.ingest_event(claims, payload, idempotency_key=idempotency_key)
        metrics.add_metric(name="EventIngested", unit=MetricUnit.Count, value=1)
        return _build_response(200, {"ok": True, **result})
    except PayloadTooLargeError:
        return _build_response(413, {"message": "Payload too large"})
    except ValidationError as exc:
        return _build_response(400, {"message": str(exc)})
    except UnauthorizedError:
        return _build_response(401, {"message": "Unauthorized"})
    except ForbiddenError:
        return _build_response(403, {"message": "Forbidden"})
    except ConflictError as exc:
        return _build_response(409, {"message": str(exc)})
    except Exception:
        logger.exception("Unhandled error in ingest_event")
        return _build_response(500, {"message": "Internal server error"})

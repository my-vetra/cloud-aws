from __future__ import annotations

import os

from vetra.logging import logger, tracer, with_correlation_id

SERVICE_VERSION = os.environ.get("SERVICE_VERSION", "0.1.0")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "vetra-api")


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, _context):
    with_correlation_id(event.get("headers"))
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": (
            f"{{\"status\":\"ok\",\"service\":\"{SERVICE_NAME}\",\"version\":\"{SERVICE_VERSION}\"}}"
        ),
    }

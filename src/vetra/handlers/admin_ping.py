from __future__ import annotations

import json

from vetra.auth import get_claims, require_groups
from vetra.errors import ForbiddenError, UnauthorizedError
from vetra.logging import logger, tracer, with_correlation_id


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, _context):
    with_correlation_id(event.get("headers"))
    try:
        claims = get_claims(event)
        require_groups(claims, {"admin"})
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "pong", "groups": claims.get("cognito:groups")}),
        }
    except UnauthorizedError:
        return {"statusCode": 401, "body": json.dumps({"message": "Unauthorized"})}
    except ForbiddenError:
        return {"statusCode": 403, "body": json.dumps({"message": "Forbidden"})}
    except Exception:
        logger.exception("Unhandled error in admin_ping")
        return {"statusCode": 500, "body": json.dumps({"message": "Internal server error"})}

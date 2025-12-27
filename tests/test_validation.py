import os

import pytest
from vetra.errors import PayloadTooLargeError, ValidationError
from vetra.validation import enforce_max_body_size, parse_json_body, validate_event_payload
from vetra.handlers import ingest_event

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("MAX_BODY_BYTES", "65536")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")


def test_validate_event_schema_rejects_missing_field():
    bad_payload = {"eventType": "click", "deviceId": "d1"}
    with pytest.raises(ValidationError):
        validate_event_payload(bad_payload)


def test_enforce_max_body_size_raises():
    with pytest.raises(PayloadTooLargeError):
        enforce_max_body_size("x" * 100, 10)


def test_parse_json_body_rejects():
    with pytest.raises(ValidationError):
        parse_json_body("not-json")


def test_ingest_handler_schema_rejection():
    event = {
        "headers": {},
        "body": "{}",
        "isBase64Encoded": False,
        "requestContext": {"authorizer": {"claims": {"sub": "user-1", "cognito:groups": "user"}}},
    }
    response = ingest_event.handler(event, None)
    assert response["statusCode"] == 400

import json
import os

import pytest
from vetra.handlers import admin_ping

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("MAX_BODY_BYTES", "65536")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")


def test_admin_route_denies_non_admin():
    event = {
        "headers": {},
        "requestContext": {"authorizer": {"claims": {"sub": "123", "cognito:groups": "user"}}},
    }
    response = admin_ping.handler(event, None)
    assert response["statusCode"] == 403


def test_admin_route_allows_admin():
    event = {
        "headers": {},
        "requestContext": {"authorizer": {"claims": {"sub": "123", "cognito:groups": "admin"}}},
    }
    response = admin_ping.handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "pong"

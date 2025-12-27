import json
import os

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("MAX_BODY_BYTES", "65536")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from vetra.handlers import health


def test_health_ok():
    response = health.handler({"headers": {}}, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "ok"
    assert "service" in body

import json
import os

import boto3
import pytest
from moto import mock_dynamodb

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("MAX_BODY_BYTES", "65536")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from vetra.handlers import get_rollups, ingest_event


@pytest.fixture
def create_table():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    resource.create_table(
        TableName="test-table",
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    yield


def _ingest(ts: str, device: str):
    body = json.dumps(
        {
            "eventType": "click",
            "deviceId": device,
            "ts": ts,
            "payload": {"key": "value"},
        }
    )
    event = {
        "headers": {},
        "body": body,
        "isBase64Encoded": False,
        "requestContext": {"authorizer": {"claims": {"sub": "user-1", "cognito:groups": "user"}}},
    }
    ingest_event.handler(event, None)


@mock_dynamodb
@pytest.mark.usefixtures("create_table")
def test_rollup_query_and_gsi_path(create_table):
    _ingest("2024-01-01T00:00:00Z", "device-1")
    _ingest("2024-01-02T00:00:00Z", "device-1")

    event = {
        "headers": {},
        "queryStringParameters": {"from": "2024-01-01", "to": "2024-01-02", "deviceId": "device-1"},
        "requestContext": {"authorizer": {"claims": {"sub": "user-1", "cognito:groups": "user"}}},
    }
    response = get_rollups.handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert len(body["rollups"]) == 2
    assert len(body["events"]) == 2

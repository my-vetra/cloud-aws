import json
import os

import boto3
import pytest
from moto import mock_dynamodb

os.environ.setdefault("TABLE_NAME", "test-table")
os.environ.setdefault("MAX_BODY_BYTES", "65536")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from vetra.handlers import ingest_event


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


def _event_body(event_id: str):
    return json.dumps(
        {
            "eventId": event_id,
            "eventType": "click",
            "deviceId": "device-1",
            "ts": "2024-01-01T00:00:00Z",
            "payload": {"key": "value"},
        }
    )


@mock_dynamodb
@pytest.mark.usefixtures("create_table")
def test_duplicate_does_not_increment_rollup(create_table):
    headers = {"Idempotency-Key": "idem-1"}
    auth = {"sub": "user-1", "cognito:groups": "user"}
    event = {
        "headers": headers,
        "body": _event_body("evt-1"),
        "isBase64Encoded": False,
        "requestContext": {"authorizer": {"claims": auth}},
    }

    first = ingest_event.handler(event, None)
    second = ingest_event.handler(event, None)

    assert json.loads(first["body"])["duplicate_ignored"] is False
    assert json.loads(second["body"])["duplicate_ignored"] is True

    table = boto3.resource("dynamodb", region_name="us-east-1").Table("test-table")
    rollups = table.query(
        KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
        ExpressionAttributeValues={":pk": "TENANT#default#USER#user-1", ":sk": "ROLLUP#DAY#"},
    )
    assert rollups["Count"] == 1
    counters = rollups["Items"][0]["counters"]
    assert counters["total"] == 1
    assert counters["click"] == 1

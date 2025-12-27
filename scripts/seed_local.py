#!/usr/bin/env python3
"""Seed DynamoDB Local with sample data for manual testing."""

import os
from datetime import datetime, timezone

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "vetra-local")
ENDPOINT = os.environ.get("DDB_ENDPOINT", "http://127.0.0.1:8000")

def main():
    resource = boto3.resource("dynamodb", endpoint_url=ENDPOINT, region_name="us-east-1")
    table = resource.Table(TABLE_NAME)
    now = datetime.now(timezone.utc).isoformat()
    pk = "TENANT#default#USER#demo"
    items = [
        {
            "PK": pk,
            "SK": f"EVENT#2024-01-01#{int(datetime(2024,1,1,tzinfo=timezone.utc).timestamp()*1000)}#seed-1",
            "GSI1PK": "DEVICE#seed-device",
            "GSI1SK": f"TS#{int(datetime(2024,1,1,tzinfo=timezone.utc).timestamp()*1000)}#USER#demo",
            "eventType": "click",
            "deviceId": "seed-device",
            "ts": "2024-01-01T00:00:00Z",
            "payload": {"hello": "world"},
            "createdAt": now,
        },
        {
            "PK": pk,
            "SK": "ROLLUP#DAY#2024-01-01",
            "counters": {"click": 1, "total": 1},
            "updatedAt": now,
        },
    ]
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
    print(f"Seeded {len(items)} items into {TABLE_NAME} at {ENDPOINT}")


if __name__ == "__main__":
    main()

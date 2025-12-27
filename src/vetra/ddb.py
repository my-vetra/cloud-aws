from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any, List

import boto3
from botocore.exceptions import ClientError

from .config import get_settings
from .errors import ConflictError

settings = get_settings()


def _table():
    kwargs = {"region_name": "us-east-1"}
    if settings.ddb_endpoint:
        kwargs["endpoint_url"] = settings.ddb_endpoint
    resource = boto3.resource("dynamodb", **kwargs)
    return resource.Table(settings.table_name)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _epoch_ms(ts: str) -> int:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def ingest_event(
    claims: dict[str, Any], payload: dict[str, Any], idempotency_key: str | None = None
) -> dict[str, Any]:
    table = _table()
    user_id = claims.get("sub", "unknown")
    tenant_id = claims.get("custom:tenant") or claims.get("tenant") or "default"
    event_id = idempotency_key or payload.get("eventId") or str(uuid.uuid4())
    ts = payload["ts"]
    device_id = payload["deviceId"]
    event_type = payload["eventType"]

    epoch_ms = _epoch_ms(ts)
    day = ts.split("T")[0]

    pk = f"TENANT#{tenant_id}#USER#{user_id}"
    sk = f"EVENT#{day}#{epoch_ms}#{event_id}"
    gsi_pk = f"DEVICE#{device_id}"
    gsi_sk = f"TS#{epoch_ms}#USER#{user_id}"

    event_item = {
        "PK": pk,
        "SK": sk,
        "GSI1PK": gsi_pk,
        "GSI1SK": gsi_sk,
        "eventType": event_type,
        "deviceId": device_id,
        "ts": ts,
        "payload": payload.get("payload", {}),
        "createdAt": _now_iso(),
    }

    rollup_key = {"PK": pk, "SK": f"ROLLUP#DAY#{day}"}

    try:
        table.meta.client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": table.name,
                        "Item": event_item,
                        "ConditionExpression": "attribute_not_exists(PK)",
                    }
                },
                {
                    "Update": {
                        "TableName": table.name,
                        "Key": rollup_key,
                        "UpdateExpression": "SET updatedAt = :now ADD counters.#et :one, counters.total :one",
                        "ExpressionAttributeNames": {"#et": event_type},
                        "ExpressionAttributeValues": {":one": 1, ":now": _now_iso()},
                    }
                },
            ]
        )
        return {"duplicate_ignored": False, "eventId": event_id}
    except ClientError as err:  # pragma: no cover - exercised in tests
        if err.response["Error"].get("Code") in {"TransactionCanceledException"}:
            reasons: List[Any] = err.response["CancellationReasons"] or []
            if any(r.get("Code") == "ConditionalCheckFailed" for r in reasons):
                return {"duplicate_ignored": True, "eventId": event_id}
        raise ConflictError("Failed to ingest event") from err


def query_rollups(claims: dict[str, Any], start_date: str, end_date: str) -> list[dict[str, Any]]:
    table = _table()
    user_id = claims.get("sub", "unknown")
    tenant_id = claims.get("custom:tenant") or claims.get("tenant") or "default"
    pk = f"TENANT#{tenant_id}#USER#{user_id}"
    start_key = f"ROLLUP#DAY#{start_date}"
    end_key = f"ROLLUP#DAY#{end_date}"

    resp = table.query(
        KeyConditionExpression="PK = :pk AND SK BETWEEN :start AND :end",
        ExpressionAttributeValues={":pk": pk, ":start": start_key, ":end": end_key},
    )
    return resp.get("Items", [])


def query_events_by_device(device_id: str, limit: int = 20) -> list[dict[str, Any]]:
    table = _table()
    resp = table.query(
        IndexName="GSI1",
        KeyConditionExpression="GSI1PK = :pk",
        ExpressionAttributeValues={":pk": f"DEVICE#{device_id}"},
        Limit=limit,
        ScanIndexForward=False,
    )
    return resp.get("Items", [])

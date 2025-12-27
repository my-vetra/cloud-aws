from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    table_name: str = os.environ["TABLE_NAME"]
    max_body_bytes: int = int(os.environ.get("MAX_BODY_BYTES", "65536"))
    service_name: str = os.environ.get("SERVICE_NAME", "vetra-api")
    stage: str = os.environ.get("STAGE", "dev")
    correlation_header: str = os.environ.get("CORRELATION_HEADER", "x-correlation-id")
    ddb_endpoint: str | None = os.environ.get("DDB_ENDPOINT")


_SETTINGS: Settings | None = None


def get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings()
    return _SETTINGS

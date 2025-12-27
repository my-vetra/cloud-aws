from __future__ import annotations

import json
from importlib import resources
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError

from .errors import PayloadTooLargeError, ValidationError


def load_event_schema() -> dict:
    with resources.files("vetra.models").joinpath("event_schema.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_event_payload(payload: dict) -> None:
    schema = load_event_schema()
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        message = "; ".join(err.message for err in errors)
        raise ValidationError(message)


def parse_json_body(body: str) -> dict:
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValidationError("Invalid JSON body") from exc


def enforce_max_body_size(raw_body: str, limit: int) -> None:
    if len(raw_body.encode("utf-8")) > limit:
        raise PayloadTooLargeError("Payload exceeds configured size limit")

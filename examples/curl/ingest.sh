#!/usr/bin/env bash
BASE_URL=${BASE_URL:?set BASE_URL}
TOKEN=${TOKEN:?set TOKEN}
IDEMPOTENCY_KEY=${IDEMPOTENCY_KEY:-demo-1}

curl -s -X POST "$BASE_URL/v1/events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
  -d '{"eventType":"click","deviceId":"device-1","ts":"2024-01-01T00:00:00Z","payload":{"foo":"bar"}}' | jq .

#!/usr/bin/env bash
BASE_URL=${BASE_URL:?set BASE_URL}
TOKEN=${TOKEN:?set TOKEN}
FROM=${FROM:-2024-01-01}
TO=${TO:-2024-01-07}
DEVICE_ID=${DEVICE_ID:-device-1}

curl -s "$BASE_URL/v1/rollups?from=${FROM}&to=${TO}&deviceId=${DEVICE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" | jq .

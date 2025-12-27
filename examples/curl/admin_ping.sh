#!/usr/bin/env bash
BASE_URL=${BASE_URL:?set BASE_URL}
TOKEN=${TOKEN:?set TOKEN}

curl -s "$BASE_URL/v1/admin/ping" -H "Authorization: Bearer ${TOKEN}" | jq .

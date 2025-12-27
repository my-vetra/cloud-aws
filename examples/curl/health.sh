#!/usr/bin/env bash
BASE_URL=${BASE_URL:?set BASE_URL}
curl -s "$BASE_URL/v1/health" | jq .

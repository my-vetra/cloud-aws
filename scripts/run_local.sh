#!/usr/bin/env bash
set -euo pipefail

TABLE_NAME=${TABLE_NAME:-vetra-local}
MAX_BODY_BYTES=${MAX_BODY_BYTES:-65536}
DDB_CONTAINER=${DDB_CONTAINER:-vetra-dynamodb-local}
DDB_PORT=${DDB_PORT:-8000}
DDB_ENDPOINT=http://127.0.0.1:${DDB_PORT}

if ! docker ps --format '{{.Names}}' | grep -q "${DDB_CONTAINER}"; then
  echo "Starting DynamoDB Local in container ${DDB_CONTAINER}"
  docker run -d --name "${DDB_CONTAINER}" -p ${DDB_PORT}:8000 amazon/dynamodb-local > /dev/null
fi

aws dynamodb create-table \
  --table-name "${TABLE_NAME}" \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S AttributeName=GSI1PK,AttributeType=S AttributeName=GSI1SK,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes "IndexName=GSI1,KeySchema=[{AttributeName=GSI1PK,KeyType=HASH},{AttributeName=GSI1SK,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
  --endpoint-url "${DDB_ENDPOINT}" \
  --region us-east-1 >/dev/null 2>&1 || true

env_file=$(mktemp)
cat >"${env_file}" <<EOF
{
  "IngestEventFunction": {
    "TABLE_NAME": "${TABLE_NAME}",
    "MAX_BODY_BYTES": "${MAX_BODY_BYTES}",
    "DDB_ENDPOINT": "${DDB_ENDPOINT}",
    "STAGE": "local",
    "SERVICE_NAME": "vetra-api"
  },
  "GetRollupsFunction": {
    "TABLE_NAME": "${TABLE_NAME}",
    "MAX_BODY_BYTES": "${MAX_BODY_BYTES}",
    "DDB_ENDPOINT": "${DDB_ENDPOINT}",
    "STAGE": "local",
    "SERVICE_NAME": "vetra-api"
  },
  "AdminPingFunction": {
    "TABLE_NAME": "${TABLE_NAME}",
    "MAX_BODY_BYTES": "${MAX_BODY_BYTES}",
    "DDB_ENDPOINT": "${DDB_ENDPOINT}",
    "STAGE": "local",
    "SERVICE_NAME": "vetra-api"
  },
  "HealthFunction": {
    "TABLE_NAME": "${TABLE_NAME}",
    "MAX_BODY_BYTES": "${MAX_BODY_BYTES}",
    "DDB_ENDPOINT": "${DDB_ENDPOINT}",
    "STAGE": "local",
    "SERVICE_NAME": "vetra-api"
  }
}
EOF

sam local start-api --env-vars "${env_file}" --parameter-overrides Stage=local MaxBodyBytes=${MAX_BODY_BYTES}

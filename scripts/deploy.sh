#!/usr/bin/env bash
set -euo pipefail

STACK=${STACK:-vetra-serverless}
STAGE=${STAGE:-dev}
REGION=${REGION:-us-east-1}
MAX_BODY_BYTES=${MAX_BODY_BYTES:-65536}
API_RATE=${API_RATE:-10}
API_BURST=${API_BURST:-5}
USAGE_PLAN=${USAGE_PLAN:-true}
USAGE_QUOTA=${USAGE_QUOTA:-50000}
USAGE_RATE=${USAGE_RATE:-10}
USAGE_BURST=${USAGE_BURST:-20}
HOSTED_UI_DOMAIN=${HOSTED_UI_DOMAIN:-vetra-${STAGE}}
CALLBACK_URLS=${CALLBACK_URLS:-https://example.com/callback}
LOGOUT_URLS=${LOGOUT_URLS:-https://example.com/logout}
GOOGLE_ID_PARAM=${GOOGLE_ID_PARAM:-/vetra/google/client_id}
GOOGLE_SECRET_PARAM=${GOOGLE_SECRET_PARAM:-/vetra/google/client_secret}
APPLE_ID_PARAM=${APPLE_ID_PARAM:-/vetra/apple/client_id}
APPLE_SECRET_PARAM=${APPLE_SECRET_PARAM:-/vetra/apple/client_secret}

sam deploy \
  --stack-name "${STACK}" \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region "${REGION}" \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
    Stage="${STAGE}" \
    MaxBodyBytes=${MAX_BODY_BYTES} \
    ApiRateLimit=${API_RATE} \
    ApiBurstLimit=${API_BURST} \
    EnableUsagePlan=${USAGE_PLAN} \
    UsagePlanQuota=${USAGE_QUOTA} \
    UsagePlanThrottleRate=${USAGE_RATE} \
    UsagePlanThrottleBurst=${USAGE_BURST} \
    HostedUIDomainPrefix="${HOSTED_UI_DOMAIN}" \
    CallbackURLs="${CALLBACK_URLS}" \
    LogoutURLs="${LOGOUT_URLS}" \
    GoogleClientIdParamName="${GOOGLE_ID_PARAM}" \
    GoogleClientSecretParamName="${GOOGLE_SECRET_PARAM}" \
    AppleClientIdParamName="${APPLE_ID_PARAM}" \
    AppleClientSecretParamName="${APPLE_SECRET_PARAM}"

# Architecture

This service provides a production-ready serverless backend on AWS using API Gateway, AWS Lambda, DynamoDB, and Cognito with Google/Apple federation.

## Request flow
1. Client authenticates via Cognito Hosted UI (authorization code flow) using Cognito + Google + Apple providers.
2. Client exchanges the authorization code for tokens and calls the API with `Authorization: Bearer <id_token>`.
3. API Gateway uses a Cognito authorizer to validate the JWT, enforce rate limits, and run body validation against the `EventPayload` JSON Schema.
4. Lambda handlers receive verified claims, enforce RBAC, validate payloads again with `jsonschema`, and write to DynamoDB.
5. Ingestion uses `TransactWriteItems` to atomically put the event item and increment a daily rollup item. Duplicate event IDs are ignored without double-counting.
6. Rollup queries read by PK/SK and optionally query the GSI for device-scoped event history.
7. CloudWatch captures logs, metrics, and X-Ray traces; alarms fire on Lambda errors, duration p95, API 5XX, and throttles.

## Operational guardrails
- Stage throttling via API Gateway MethodSettings; optional Usage Plan with API keys and quotas.
- Payload size controls: API Gateway documented limit plus Lambda hard check using `MAX_BODY_BYTES`.
- Structured JSON logging with correlation IDs via Lambda Powertools; tracing enabled by default.
- Least-privilege IAM (DynamoDB CRUD only for app functions).
- Log retention set to 14 days; CloudWatch alarms for errors, latency, and throttles.

## Local development
- DynamoDB Local + `sam local start-api` (see `scripts/run_local.sh`).
- Schema validation and RBAC enforced locally with mock claims and bearer tokens.

# API Reference

Base URL: `https://{apiId}.execute-api.{region}.amazonaws.com/{stage}`

## GET /v1/health (public)
- Returns service status and version.

Example:
```bash
curl "$BASE_URL/v1/health"
```

## POST /v1/events (protected)
- Auth: `Authorization: Bearer <JWT>` (id token)
- Body schema: `EventPayload` (JSON Schema enforced at API Gateway and Lambda).
- Headers: optional `Idempotency-Key` for deduplication.
- Behavior: TransactWriteItems inserts event + rollup update atomically. Duplicate returns `duplicate_ignored=true`.
- Errors: 400 schema validation, 401/403 RBAC, 413 payload too large, 409 conflict.

Example:
```bash
curl -X POST "$BASE_URL/v1/events" \
  -H "Authorization: Bearer $ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"eventType":"click","deviceId":"device-1","ts":"2024-01-01T00:00:00Z","payload":{"foo":"bar"}}'
```

## GET /v1/rollups (protected)
- Query: `from=YYYY-MM-DD&to=YYYY-MM-DD` (required), `deviceId` (optional to fetch recent events via GSI1).
- Returns rollup items for the authenticated user (and tenant) plus recent events for the device when provided.

## GET /v1/admin/ping (admin-only)
- Auth: JWT must include `cognito:groups` containing `admin`.
- Returns 403 for non-admin users.

## Error shape
```json
{"message": "<description>"}
```

## Limits & throttles
- Stage throttling: `ApiRateLimit`/`ApiBurstLimit` parameters.
- Optional Usage Plan with API key + quota/throttle when `EnableUsagePlan=true`.
- Payload size: API Gateway max 10MB (documented); Lambda hard cap via `MAX_BODY_BYTES`.
